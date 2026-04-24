// JCD Foundation — branded single-phrase gate
// Runs at the edge on every request (see netlify.toml).
// No browser basic-auth popup; renders an on-brand JCD-styled unlock page
// and stores unlock state in a 30-day cookie.

import type { Context } from "https://edge.netlify.com";

const PASSWORD = "goodkids";
const COOKIE_NAME = "jcd_unlock";
const COOKIE_MAX_AGE = 60 * 60 * 24 * 30; // 30 days

const SECURITY_HEADERS: Record<string, string> = {
  "Cache-Control": "private, no-store",
  "X-Robots-Tag": "noindex, nofollow",
};

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function gatePage(error?: string): string {
  const errBlock = error
    ? `<div class="gate-error">${escapeHtml(error)}</div>`
    : "";
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="robots" content="noindex,nofollow" />
<title>JCD Foundation — private preview</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Montserrat:wght@400;500;600;700;800;900&family=Roboto+Mono:wght@400;500&family=Caveat:wght@500;700&display=swap" rel="stylesheet" />
<style>
:root {
  --equipto-blue: #0E2A58;
  --white: #FFFFFF;
  --deep-charcoal: #111827;
  --brass-gold: #C5963A;
  --safety-orange: #E8600A;
  --font-primary: 'Montserrat', sans-serif;
  --font-display: 'Archivo Black', 'Montserrat', sans-serif;
  --font-mono: 'Roboto Mono', monospace;
  --font-hand: 'Caveat', cursive;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; min-height: 100%; }
body {
  font-family: var(--font-primary);
  background: var(--deep-charcoal);
  color: var(--white);
  overflow-x: hidden;
  position: relative;
  -webkit-font-smoothing: antialiased;
  line-height: 1.5;
}
body::before {
  content: '';
  position: fixed;
  inset: 0;
  background:
    radial-gradient(ellipse at 18% 22%, rgba(232, 96, 10, 0.22), transparent 52%),
    radial-gradient(ellipse at 82% 78%, rgba(197, 150, 58, 0.14), transparent 58%),
    linear-gradient(180deg, var(--deep-charcoal), var(--equipto-blue) 68%, var(--deep-charcoal));
  pointer-events: none;
  z-index: 0;
}
body::after {
  content: '';
  position: fixed;
  inset: 0;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='240' height='240' filter='url(%23n)' opacity='0.55'/></svg>");
  opacity: 0.07;
  pointer-events: none;
  z-index: 0;
  mix-blend-mode: overlay;
}
.gate {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 72px 24px 120px;
  text-align: center;
}
.gate-label {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.24em;
  text-transform: uppercase;
  color: var(--brass-gold);
  margin-bottom: 28px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
}
.gate-label::before, .gate-label::after {
  content: '';
  display: inline-block;
  width: 28px;
  height: 1px;
  background: var(--brass-gold);
}
.gate h1 {
  font-family: var(--font-display);
  font-size: clamp(76px, 13vw, 180px);
  line-height: 0.86;
  letter-spacing: -0.04em;
  text-transform: uppercase;
  margin-bottom: 20px;
}
.gate h1 em {
  font-style: normal;
  color: var(--safety-orange);
}
.gate-hand {
  font-family: var(--font-hand);
  font-weight: 700;
  font-size: clamp(28px, 3.6vw, 40px);
  color: var(--brass-gold);
  line-height: 1.1;
  margin-bottom: 56px;
  transform: rotate(-1.5deg);
  display: inline-block;
}
.gate-form {
  width: 100%;
  max-width: 440px;
  display: flex;
  flex-direction: column;
  gap: 26px;
  align-items: stretch;
}
.gate-input {
  width: 100%;
  background: transparent;
  border: 0;
  border-bottom: 2px solid rgba(255,255,255,0.25);
  color: var(--white);
  font-family: var(--font-primary);
  font-weight: 600;
  font-size: 26px;
  padding: 16px 0;
  text-align: center;
  transition: border-color 0.2s;
  caret-color: var(--brass-gold);
}
.gate-input::placeholder {
  color: rgba(255,255,255,0.3);
  font-weight: 400;
  letter-spacing: 0.04em;
}
.gate-input:focus { outline: none; border-bottom-color: var(--brass-gold); }
.gate-btn {
  align-self: center;
  background: var(--safety-orange);
  color: var(--white);
  font-family: var(--font-primary);
  font-weight: 800;
  font-size: 14px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 18px 32px;
  border: 0;
  cursor: pointer;
  box-shadow: 5px 5px 0 var(--deep-charcoal);
  transition: transform 0.15s, box-shadow 0.15s;
}
.gate-btn:hover {
  transform: translate(-2px, -2px);
  box-shadow: 7px 7px 0 var(--deep-charcoal);
}
.gate-btn:active {
  transform: translate(2px, 2px);
  box-shadow: 2px 2px 0 var(--deep-charcoal);
}
.gate-error {
  font-family: var(--font-hand);
  font-weight: 700;
  font-size: clamp(22px, 2.6vw, 28px);
  color: var(--safety-orange);
  margin-top: -8px;
  transform: rotate(-1.2deg);
  text-align: center;
}
.gate-foot {
  position: absolute;
  bottom: 28px;
  left: 0; right: 0;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.35);
  text-align: center;
  padding: 0 24px;
}
.gate-foot span { color: var(--brass-gold); }
@media (max-height: 680px) {
  .gate { justify-content: flex-start; padding-top: 60px; }
  .gate-hand { margin-bottom: 36px; }
}
</style>
</head>
<body>
<main class="gate">
  <div class="gate-label">Private Preview · Password Required</div>
  <h1>Pull <em>up.</em></h1>
  <p class="gate-hand">one word gets you in.</p>
  <form class="gate-form" action="/_gate" method="POST" autocomplete="off">
    <input class="gate-input" type="password" name="password" placeholder="the password" autofocus required autocapitalize="off" autocorrect="off" spellcheck="false" />
    ${errBlock}
    <button class="gate-btn" type="submit">Let me in →</button>
  </form>
  <div class="gate-foot">JCD Foundation · <span>Private Preview</span> · 2026</div>
</main>
</body>
</html>`;
}

export default async (request: Request, context: Context) => {
  const url = new URL(request.url);

  // Handle the gate-form submission.
  if (request.method === "POST" && url.pathname === "/_gate") {
    let provided = "";
    try {
      const form = await request.formData();
      provided = String(form.get("password") ?? "");
    } catch {
      provided = "";
    }

    if (provided === PASSWORD) {
      return new Response(null, {
        status: 303,
        headers: {
          Location: "/",
          "Set-Cookie": `${COOKIE_NAME}=${PASSWORD}; Path=/; Max-Age=${COOKIE_MAX_AGE}; Secure; HttpOnly; SameSite=Lax`,
          ...SECURITY_HEADERS,
        },
      });
    }

    return new Response(gatePage("not quite. try again."), {
      status: 401,
      headers: {
        "content-type": "text/html; charset=utf-8",
        ...SECURITY_HEADERS,
      },
    });
  }

  // Check unlock cookie.
  const cookieHeader = request.headers.get("cookie") ?? "";
  const unlocked = cookieHeader
    .split(";")
    .map((c) => c.trim())
    .some((c) => c === `${COOKIE_NAME}=${PASSWORD}`);

  if (unlocked) {
    const response = await context.next();
    // Prevent caching/indexing of unlocked pages.
    response.headers.set("Cache-Control", "private, no-store");
    response.headers.set("X-Robots-Tag", "noindex, nofollow");
    return response;
  }

  return new Response(gatePage(), {
    status: 200,
    headers: {
      "content-type": "text/html; charset=utf-8",
      ...SECURITY_HEADERS,
    },
  });
};

export const config = { path: "/*" };
