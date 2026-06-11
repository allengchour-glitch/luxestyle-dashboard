/**
 * aban news — Signup-/Double-Opt-in-Backend (Cloudflare Worker, serverlos).
 *
 * Routen:
 *   POST /subscribe   { email, source }   -> speichert "pending" + sendet Bestaetigungsmail
 *   GET  /confirm?e=&t=                    -> bestaetigt (Double-Opt-in) + sendet Welcome
 *   GET  /abmelden?e=&t=                   -> Abmeldung
 *   GET  /export?key=ADMIN_KEY             -> CSV der aktiven Abonnenten (fuer aban_send.py)
 *
 * Warum hier: abannews.com laeuft auf Cloudflare -> Worker passt nahtlos, kein eigener Server.
 *
 * Setup (Cloudflare Dashboard -> Workers):
 *   1) KV-Namespace anlegen, als Binding "ABAN_SUBS" einbinden.
 *   2) Variablen/Secrets:
 *        UNSUB_SECRET   = gleiches Geheimnis wie aban_send.py/aban_welcome.py (Token-Kompatibilitaet)
 *        RESEND_API_KEY = API-Key des Mail-Providers (Resend; Brevo-Variante s. unten)
 *        MAIL_FROM      = z.B. "aban news <news@abannews.com>"
 *        ADMIN_KEY      = beliebiges Geheimnis fuer /export
 *   3) Route: abannews.com/subscribe, /confirm, /abmelden, /export  (oder als eigene Subdomain).
 *   4) Signup-Widget (signup-widget.html) data-endpoint auf die /subscribe-URL setzen.
 *
 * Mail-Provider: Default Resend (api.resend.com). Fuer Brevo siehe sendBrevo() unten.
 */

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (req.method === "OPTIONS") return new Response(null, { headers: CORS });
    try {
      if (url.pathname === "/subscribe" && req.method === "POST") return subscribe(req, env);
      if (url.pathname === "/confirm") return confirm(url, env);
      if (url.pathname === "/abmelden") return unsubscribe(url, env);
      if (url.pathname === "/export") return exportCsv(url, env);
      return new Response("aban news subscribe service", { status: 200, headers: CORS });
    } catch (e) {
      return json({ ok: false, error: String(e) }, 500);
    }
  },
};

// ----------------------------------------------------------------- Helpers
function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json", ...CORS } });
}
function pageHtml(title, body) {
  return new Response(
    `<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
     <title>${title}</title></head><body style="margin:0;background:#eef1f5;font-family:-apple-system,Segoe UI,sans-serif">
     <div style="max-width:480px;margin:8vh auto;background:#fff;border-radius:16px;padding:32px 28px;text-align:center;box-shadow:0 8px 30px rgba(16,19,26,.08)">
     <div style="font:800 22px -apple-system,Segoe UI,sans-serif;color:#10131a;margin-bottom:14px">aban<span style="color:#0b5">news</span></div>
     ${body}</div></body></html>`,
    { status: 200, headers: { "Content-Type": "text/html; charset=utf-8", ...CORS } }
  );
}
function isEmail(s) { return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(s || ""); }

async function token(secret, purpose, email) {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(`${purpose}:${email.toLowerCase()}`));
  return [...new Uint8Array(sig)].map(b => b.toString(16).padStart(2, "0")).join("").slice(0, 24);
}

// ----------------------------------------------------------------- Mail (Resend default)
async function sendMail(env, to, subject, html) {
  if (!env.RESEND_API_KEY) return; // ohne Key: still skip (Anmeldung wird trotzdem gespeichert)
  await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { "Authorization": `Bearer ${env.RESEND_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({ from: env.MAIL_FROM || "aban news <onboarding@resend.dev>", to, subject, html }),
  });
}
// Brevo-Alternative (statt sendMail oben einsetzen):
// async function sendBrevo(env,to,subject,html){ await fetch("https://api.brevo.com/v3/smtp/email",{method:"POST",
//   headers:{"api-key":env.BREVO_API_KEY,"Content-Type":"application/json"},
//   body:JSON.stringify({sender:{email:"news@abannews.com",name:"aban news"},to:[{email:to}],subject,htmlContent:html})});}

const BASE = "https://abannews.com";
function confirmMail(link) {
  return `<div style="font-family:-apple-system,Segoe UI,sans-serif;max-width:520px;margin:0 auto">
    <h1 style="font:700 22px Georgia,serif;color:#10131a">Fast geschafft — bitte bestaetigen</h1>
    <p style="color:#3a4150;font-size:15px;line-height:1.6">Du hast dich fuer <b>aban news</b> angemeldet — taeglich KI &amp; Krypto in 5 Minuten. Klicke kurz zur Bestaetigung:</p>
    <p><a href="${link}" style="display:inline-block;background:#0b5;color:#fff;font-weight:700;text-decoration:none;padding:13px 26px;border-radius:8px">Anmeldung bestaetigen</a></p>
    <p style="color:#8a93a3;font-size:12px">Nicht angefordert? Ignoriere diese Mail.</p></div>`;
}
function welcomeMail(unsub) {
  return `<div style="font-family:-apple-system,Segoe UI,sans-serif;max-width:520px;margin:0 auto">
    <h1 style="font:700 22px Georgia,serif;color:#10131a">Willkommen bei aban news</h1>
    <p style="color:#3a4150;font-size:15px;line-height:1.6">Ab jetzt bekommst du jeden Morgen die wichtigsten KI- &amp; Krypto-News kompakt auf Deutsch — mit Markt-Snapshot und Einordnung. Sonntags zusaetzlich der Pro Deep-Dive.</p>
    <p style="color:#9aa3b2;font-size:12px">Jederzeit <a href="${unsub}" style="color:#9aa3b2">abmelden</a>.</p></div>`;
}

// ----------------------------------------------------------------- Routes
async function subscribe(req, env) {
  const { email } = await req.json().catch(() => ({}));
  if (!isEmail(email)) return json({ ok: false, error: "invalid email" }, 400);
  const e = email.toLowerCase();
  const existing = await env.ABAN_SUBS.get(e, "json");
  if (existing && existing.status === "active") return json({ ok: true, status: "already" });
  const t = await token(env.UNSUB_SECRET, "confirm", e);
  await env.ABAN_SUBS.put(e, JSON.stringify({ status: "pending", ts: Date.now() }));
  const link = `${BASE}/confirm?e=${encodeURIComponent(e)}&t=${t}`;
  await sendMail(env, e, "Bitte bestaetige deine aban-news-Anmeldung", confirmMail(link));
  return json({ ok: true, status: "pending" });
}

async function confirm(url, env) {
  const e = (url.searchParams.get("e") || "").toLowerCase();
  const t = url.searchParams.get("t") || "";
  if (!isEmail(e) || t !== (await token(env.UNSUB_SECRET, "confirm", e)))
    return pageHtml("Link ungueltig", `<p style="color:#3a4150">Dieser Bestaetigungslink ist ungueltig oder abgelaufen.</p>`);
  await env.ABAN_SUBS.put(e, JSON.stringify({ status: "active", edition: "free", ts: Date.now() }));
  const ut = await token(env.UNSUB_SECRET, "unsub", e);
  await sendMail(env, e, "Willkommen bei aban news", welcomeMail(`${BASE}/abmelden?e=${encodeURIComponent(e)}&t=${ut}`));
  return pageHtml("Bestaetigt", `<h2 style="color:#10131a;font-family:Georgia,serif">Anmeldung bestaetigt</h2>
    <p style="color:#3a4150">Willkommen bei aban news. Deine erste Ausgabe kommt morgen frueh.</p>
    <p><a href="${BASE}" style="color:#0b5">Zur Startseite</a></p>`);
}

async function unsubscribe(url, env) {
  const e = (url.searchParams.get("e") || "").toLowerCase();
  const t = url.searchParams.get("t") || "";
  if (!isEmail(e) || t !== (await token(env.UNSUB_SECRET, "unsub", e)))
    return pageHtml("Link ungueltig", `<p style="color:#3a4150">Dieser Abmelde-Link ist ungueltig.</p>`);
  await env.ABAN_SUBS.put(e, JSON.stringify({ status: "unsubscribed", ts: Date.now() }));
  return pageHtml("Abgemeldet", `<p style="color:#3a4150">Du wurdest abgemeldet. Schade, dass du gehst.</p>`);
}

async function exportCsv(url, env) {
  if ((url.searchParams.get("key") || "") !== env.ADMIN_KEY) return new Response("forbidden", { status: 403 });
  const rows = ["email,edition,status,joined"];
  let cursor;
  do {
    const list = await env.ABAN_SUBS.list({ cursor });
    for (const k of list.keys) {
      const v = await env.ABAN_SUBS.get(k.name, "json");
      if (v && v.status === "active")
        rows.push(`${k.name},${v.edition || "free"},active,${new Date(v.ts || Date.now()).toISOString().slice(0, 10)}`);
    }
    cursor = list.list_complete ? null : list.cursor;
  } while (cursor);
  return new Response(rows.join("\n"), { headers: { "Content-Type": "text/csv", ...CORS } });
}
