// JCD Foundation — site-wide HTTP Basic Auth gate
// Runs at the edge on every request (see netlify.toml).
// Password is read from the SITE_PASSWORD env var in the Netlify dashboard.
// Username is ignored — any value works, only the password is checked.

import type { Context } from "https://edge.netlify.com";

export default async (request: Request, _context: Context) => {
  const expectedPassword = Deno.env.get("SITE_PASSWORD");

  // Fail closed: if no password is configured, block the site entirely
  // rather than silently exposing it.
  if (!expectedPassword) {
    return new Response(
      "Site password not configured. Set SITE_PASSWORD in Netlify environment variables.",
      { status: 503, headers: { "content-type": "text/plain" } }
    );
  }

  const authHeader = request.headers.get("authorization");

  if (authHeader?.startsWith("Basic ")) {
    try {
      const decoded = atob(authHeader.slice(6));
      const colonIdx = decoded.indexOf(":");
      const providedPassword = colonIdx === -1 ? decoded : decoded.slice(colonIdx + 1);
      if (providedPassword === expectedPassword) {
        // Correct — let the request through to the static file / next handler.
        return;
      }
    } catch {
      // fall through to 401
    }
  }

  return new Response("Authentication required.", {
    status: 401,
    headers: {
      "WWW-Authenticate": 'Basic realm="JCD Foundation — preview", charset="UTF-8"',
      "content-type": "text/plain",
    },
  });
};

export const config = { path: "/*" };
