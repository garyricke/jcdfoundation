// JCD Foundation — application review tool API (Netlify Function v2)
// --------------------------------------------------------------------------
// Backs /review. Same pattern as comments.mjs: the Supabase service_role key
// stays here, the browser never touches the database, and the whole site
// (this function included) sits behind the /* gate edge function.
//
// On top of the site gate, every call must carry the review password in an
// `x-review-key` header (Netlify env var REVIEW_PASSWORD).
//
// Pilot sign-in is "pick your name": the client says who is acting and this
// function checks that person exists and has the role the action needs. That
// is NOT real authentication — swap in individual logins before real
// applicant data arrives (see plan/admin-review-tool-spec-2026-10-13.md).
//
// Required Netlify environment variables:
//   SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, REVIEW_PASSWORD
//
// Endpoints:
//   GET  ?action=bootstrap          -> { reviewers, settings, applications }
//   GET  ?action=app&id=<app_id>    -> { application, letters, recommendations, notes, overrides, audit }
//   POST { action, actor, ... }     -> see HANDLERS below

const SUPABASE_URL = process.env.SUPABASE_URL;
const SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
const REVIEW_PASSWORD = process.env.REVIEW_PASSWORD;

const RECOMMENDATIONS = ['reviewed', 'tier1', 'tier2', 'decline'];
const DECISIONS = ['fund', 'fund_tier2', 'decline', 'hold'];

const LIST_COLS = [
  'id', 'submitted_at', 'first_name', 'last_name', 'city', 'zip', 'school', 'homeschool_area',
  'grad_date', 'focus_area', 'profession', 'study_level', 'institution', 'annual_cost',
  'transcript_received', 'cost_estimate_received', 'urgent', 'ai_flag', 'final_decision',
  'award_amount', 'is_sample', 'data->career_goal',
  'review_letters(count)', 'review_notes(count)', 'review_flag_overrides(count)',
  'review_recommendations(reviewer_id,recommendation)'
].join(',');

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { 'content-type': 'application/json', 'cache-control': 'no-store' }
  });
}

function sb(path, init = {}) {
  return fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    ...init,
    headers: {
      apikey: SERVICE_KEY,
      Authorization: `Bearer ${SERVICE_KEY}`,
      'Content-Type': 'application/json',
      ...(init.headers || {})
    }
  });
}

async function sbJson(path, init) {
  const r = await sb(path, init);
  const text = await r.text();
  if (!r.ok) throw Object.assign(new Error(text || r.statusText), { status: r.status });
  return text ? JSON.parse(text) : null;
}

// Constant-time string compare so the password check doesn't leak by timing.
function safeEqual(a, b) {
  a = String(a || ''); b = String(b || '');
  let diff = a.length ^ b.length;
  for (let i = 0; i < Math.max(a.length, b.length); i++) {
    diff |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0);
  }
  return diff === 0;
}

const enc = encodeURIComponent;

async function getReviewer(id) {
  if (!id) return null;
  const rows = await sbJson(`review_reviewers?id=eq.${enc(id)}&select=*`);
  return rows && rows[0] ? rows[0] : null;
}

async function getAppMeta(id) {
  const rows = await sbJson(`review_applications?id=eq.${enc(id)}&select=id,is_sample`);
  return rows && rows[0] ? rows[0] : null;
}

async function audit(actor, app, action, detail) {
  await sb('review_audit', {
    method: 'POST',
    body: JSON.stringify({
      actor: actor.id, app_id: app ? app.id : null, action, detail: detail || {},
      is_sample: app ? !!app.is_sample : !!actor.is_sample
    })
  });
}

function bad(msg, status = 400) {
  return Object.assign(new Error(msg), { status });
}

function patchApp(id, fields) {
  return sbJson(`review_applications?id=eq.${enc(id)}`, {
    method: 'PATCH',
    headers: { Prefer: 'return=minimal' },
    body: JSON.stringify(fields)
  });
}

// Every handler gets (body, actor, app) and returns a JSON-able result.
const HANDLERS = {
  async recommend(b, actor, app) {
    if (b.recommendation === null) {
      await sbJson(`review_recommendations?app_id=eq.${enc(app.id)}&reviewer_id=eq.${enc(actor.id)}`, {
        method: 'DELETE', headers: { Prefer: 'return=minimal' }
      });
    } else {
      if (!RECOMMENDATIONS.includes(b.recommendation)) throw bad('Unknown recommendation.');
      await sbJson('review_recommendations?on_conflict=app_id,reviewer_id', {
        method: 'POST',
        headers: { Prefer: 'resolution=merge-duplicates,return=minimal' },
        body: JSON.stringify({
          app_id: app.id, reviewer_id: actor.id,
          recommendation: b.recommendation, updated_at: new Date().toISOString()
        })
      });
    }
    await audit(actor, app, 'recommendation', { recommendation: b.recommendation });
    return { ok: true };
  },

  async note(b, actor, app) {
    const body = String(b.body || '').trim();
    if (!body) throw bad('Note is empty.');
    if (body.length > 4000) throw bad('Note is too long (4,000 characters max).');
    const rows = await sbJson('review_notes', {
      method: 'POST',
      headers: { Prefer: 'return=representation' },
      body: JSON.stringify({ app_id: app.id, reviewer_id: actor.id, body })
    });
    await audit(actor, app, 'note', { length: body.length });
    return { note: rows[0] };
  },

  async checklist(b, actor, app) {
    const allowed = ['transcript_received', 'cost_estimate_received'];
    if (!allowed.includes(b.field)) throw bad('Unknown checklist item.');
    await patchApp(app.id, { [b.field]: !!b.value });
    await audit(actor, app, 'checklist', { field: b.field, value: !!b.value });
    return { ok: true };
  },

  async urgent(b, actor, app) {
    if (!['final', 'admin'].includes(actor.role)) throw bad('Only Bob or Gary can mark a case urgent.', 403);
    const note = b.value ? String(b.note || '').slice(0, 1000) : null;
    await patchApp(app.id, { urgent: !!b.value, urgent_note: note });
    await audit(actor, app, 'urgent', { value: !!b.value, note });
    return { ok: true };
  },

  async decision(b, actor, app) {
    if (actor.role !== 'final') throw bad('Only Bob sets the final decision.', 403);
    const clearing = b.final_decision === null;
    if (!clearing && !DECISIONS.includes(b.final_decision)) throw bad('Unknown decision.');
    const amount = b.award_amount === '' || b.award_amount == null ? null : Number(b.award_amount);
    if (amount !== null && !(amount >= 0 && amount < 10000000)) throw bad('Award amount looks wrong.');
    const fields = clearing
      ? { final_decision: null, award_amount: null, payee: null, decided_by: null, decided_at: null }
      : {
          final_decision: b.final_decision,
          award_amount: ['fund', 'fund_tier2'].includes(b.final_decision) ? amount : null,
          payee: String(b.payee || '').slice(0, 300) || null,
          decided_by: actor.id,
          decided_at: new Date().toISOString()
        };
    await patchApp(app.id, fields);
    await audit(actor, app, 'final_decision', fields);
    return { ok: true };
  },

  async flag_override(b, actor, app) {
    const reason = String(b.reason || '').trim().slice(0, 1000);
    await sbJson('review_flag_overrides', {
      method: 'POST',
      headers: { Prefer: 'return=minimal' },
      body: JSON.stringify({ app_id: app.id, reviewer_id: actor.id, reason: reason || null })
    });
    await audit(actor, app, 'flag_override', { reason });
    return { ok: true };
  },

  async settings(b, actor) {
    if (!['final', 'admin'].includes(actor.role)) throw bad('Only Bob or Gary can change settings.', 403);
    if (b.key !== 'zip_tiers') throw bad('Unknown setting.');
    const clean = (list) => [...new Set((Array.isArray(list) ? list : [])
      .map((z) => String(z).trim()).filter((z) => /^\d{5}$/.test(z)))].sort();
    const value = { core: clean(b.value && b.value.core), edge: clean(b.value && b.value.edge),
                    placeholder: false };
    await sbJson('review_settings?on_conflict=key', {
      method: 'POST',
      headers: { Prefer: 'resolution=merge-duplicates,return=minimal' },
      body: JSON.stringify({ key: 'zip_tiers', value, updated_at: new Date().toISOString() })
    });
    await audit(actor, null, 'settings', { key: b.key, value });
    return { value };
  }
};

export default async (req) => {
  if (!SUPABASE_URL || !SERVICE_KEY || !REVIEW_PASSWORD) {
    return json({ error: 'The review tool is not configured on the server.' }, 500);
  }
  if (!safeEqual(req.headers.get('x-review-key'), REVIEW_PASSWORD)) {
    return json({ error: 'Wrong review password.' }, 401);
  }

  try {
    if (req.method === 'GET') {
      const url = new URL(req.url);
      const action = url.searchParams.get('action');

      if (action === 'bootstrap') {
        const [reviewers, settings, applications] = await Promise.all([
          sbJson('review_reviewers?select=*&order=role.asc,name.asc'),
          sbJson('review_settings?select=*'),
          sbJson(`review_applications?select=${LIST_COLS}&order=submitted_at.desc`)
        ]);
        return json({ reviewers, settings, applications });
      }

      if (action === 'app') {
        const id = url.searchParams.get('id') || '';
        const q = `app_id=eq.${enc(id)}`;
        const [apps, letters, recommendations, notes, overrides, auditRows] = await Promise.all([
          sbJson(`review_applications?id=eq.${enc(id)}&select=*`),
          sbJson(`review_letters?${q}&select=*&order=received_at.asc`),
          sbJson(`review_recommendations?${q}&select=*&order=updated_at.asc`),
          sbJson(`review_notes?${q}&select=*&order=created_at.asc`),
          sbJson(`review_flag_overrides?${q}&select=*&order=created_at.asc`),
          sbJson(`review_audit?${q}&select=*&order=at.desc&limit=100`)
        ]);
        if (!apps[0]) return json({ error: 'Application not found.' }, 404);
        return json({ application: apps[0], letters, recommendations, notes, overrides, audit: auditRows });
      }

      return json({ error: 'Unknown action.' }, 400);
    }

    if (req.method === 'POST') {
      let body;
      try { body = await req.json(); } catch { return json({ error: 'Bad JSON.' }, 400); }
      const handler = HANDLERS[body.action];
      if (!handler) return json({ error: 'Unknown action.' }, 400);

      const actor = await getReviewer(body.actor);
      if (!actor) return json({ error: 'Pick who is reviewing first.' }, 403);

      let app = null;
      if (body.action !== 'settings') {
        app = await getAppMeta(body.app_id);
        if (!app) return json({ error: 'Application not found.' }, 404);
      }
      return json(await handler(body, actor, app));
    }

    return json({ error: 'Method not allowed.' }, 405);
  } catch (err) {
    return json({ error: err.message || 'Server error.' }, err.status || 500);
  }
};

export const config = { path: '/api/review' };
