// JCD Foundation — comments proxy (Netlify Function v2)
// --------------------------------------------------------------------------
// Holds the Supabase key server-side so it never reaches the browser, and is
// itself fronted by the /* gate edge function — so only unlocked visitors can
// reach it. Talks to Supabase via its REST API (no SDK / no npm install).
//
// Required Netlify environment variables:
//   SUPABASE_URL                e.g. https://xxxx.supabase.co
//   SUPABASE_SERVICE_ROLE_KEY   service_role key (bypasses RLS; stays here)
//
// Endpoints:
//   GET  ?page=<slug>                              -> { annotations: [ {…, comments:[…] } ] }
//   POST { type:'annotation', annotation:{…} }     -> { annotation: {…, comments:[] } }
//   POST { type:'comment', annotation_id, comment }-> { comment: {…} }

const SUPABASE_URL = process.env.SUPABASE_URL;
const SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

const ANN_COLS = ['page', 'quote', 'prefix', 'suffix', 'start_offset', 'color', 'author'];
const COMMENT_COLS = ['annotation_id', 'author', 'body'];

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { 'content-type': 'application/json', 'cache-control': 'no-store' }
  });
}

function pick(obj, cols) {
  const out = {};
  for (const c of cols) if (obj[c] !== undefined && obj[c] !== null) out[c] = obj[c];
  return out;
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

export default async (req) => {
  if (!SUPABASE_URL || !SERVICE_KEY) {
    return json({ error: 'Supabase env vars are not configured.' }, 500);
  }

  try {
    if (req.method === 'GET') {
      const page = new URL(req.url).searchParams.get('page') || '';
      const r = await sb(
        `annotations?page=eq.${encodeURIComponent(page)}&select=*,comments(*)&order=created_at.asc`
      );
      if (!r.ok) return json({ error: await r.text() }, r.status);
      const annotations = await r.json();
      // sort each thread oldest-first
      for (const a of annotations) {
        if (Array.isArray(a.comments)) {
          a.comments.sort((x, y) => new Date(x.created_at) - new Date(y.created_at));
        }
      }
      return json({ annotations });
    }

    if (req.method === 'POST') {
      const body = await req.json();

      if (body.type === 'annotation') {
        const row = pick(body.annotation || {}, ANN_COLS);
        if (!row.page || !row.quote) return json({ error: 'page and quote are required' }, 400);
        const r = await sb('annotations', {
          method: 'POST',
          headers: { Prefer: 'return=representation' },
          body: JSON.stringify(row)
        });
        if (!r.ok) return json({ error: await r.text() }, r.status);
        const rows = await r.json();
        const annotation = Array.isArray(rows) ? rows[0] : rows;
        annotation.comments = [];
        return json({ annotation });
      }

      if (body.type === 'comment') {
        const row = pick({ ...(body.comment || {}), annotation_id: body.annotation_id }, COMMENT_COLS);
        if (!row.annotation_id || !row.body) return json({ error: 'annotation_id and body are required' }, 400);
        const r = await sb('comments', {
          method: 'POST',
          headers: { Prefer: 'return=representation' },
          body: JSON.stringify(row)
        });
        if (!r.ok) return json({ error: await r.text() }, r.status);
        const rows = await r.json();
        return json({ comment: Array.isArray(rows) ? rows[0] : rows });
      }

      return json({ error: 'Unknown POST type' }, 400);
    }

    return json({ error: 'Method not allowed' }, 405);
  } catch (err) {
    return json({ error: String(err && err.message || err) }, 500);
  }
};
