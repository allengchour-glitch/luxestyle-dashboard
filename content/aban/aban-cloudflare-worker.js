/**
 * aban news — Signup-/Double-Opt-in-/Referral-Backend (Cloudflare Worker, serverlos).
 *
 * Routen:
 *   POST /subscribe   { email, source, ref }  -> "pending" + Bestaetigungsmail (ref = Empfehlungs-Code)
 *   GET  /confirm?e=&t=                        -> Double-Opt-in + Welcome (mit persoenlichem Referral-Link)
 *                                                 + schreibt dem Werber eine Empfehlung gut (Meilensteine)
 *   GET  /status?e=&t=                         -> Referral-Stand (Anzahl, Share-Link, naechster Meilenstein)
 *   GET  /abmelden?e=&t=                       -> Abmeldung
 *   GET  /export?key=ADMIN_KEY                 -> CSV der aktiven Abonnenten (fuer aban_send.py)
 *
 * Referral-Loop (Morning-Brew-Mechanik): jeder bestaetigte Abonnent bekommt einen Link
 * abannews.com/?ref=CODE. Wer darueber andere wirbt, schaltet Pro frei:
 *   3 Werbungen -> 1 Monat Pro · 10 -> 3 Monate · 25 -> 12 Monate.
 *
 * Setup (Cloudflare -> Workers):
 *   1) KV-Namespace -> Binding "ABAN_SUBS".
 *   2) Secrets/Vars: UNSUB_SECRET (= gleich wie Python-Tools), RESEND_API_KEY, MAIL_FROM,
 *      ADMIN_KEY, optional SITE (Default https://abannews.com).
 *   3) Routen auf /subscribe /confirm /status /abmelden /export.
 *   4) Widget/Landing data-endpoint -> /subscribe; ?ref= wird automatisch mitgesendet.
 */

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};
const MILESTONES = [{ n: 3, months: 1 }, { n: 10, months: 3 }, { n: 25, months: 12 }];

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (req.method === "OPTIONS") return new Response(null, { headers: CORS });
    try {
      if (url.pathname === "/subscribe" && req.method === "POST") return subscribe(req, env);
      if (url.pathname === "/confirm") return confirm(url, env);
      if (url.pathname === "/status") return status(url, env);
      if (url.pathname === "/abmelden") return unsubscribe(url, env);
      if (url.pathname === "/export") return exportCsv(url, env);
      return new Response("aban news subscribe service", { status: 200, headers: CORS });
    } catch (e) {
      return json({ ok: false, error: String(e) }, 500);
    }
  },
};

// ----------------------------------------------------------------- Helpers
function site(env) { return env.SITE || "https://abannews.com"; }       // oeffentliche Seite (Landing, Share-Link)
function api(env) { return env.API_BASE || "https://api.abannews.com"; } // Worker-Routen (subscribe/confirm/status/abmelden)
function json(o, s = 200) { return new Response(JSON.stringify(o), { status: s, headers: { "Content-Type": "application/json", ...CORS } }); }
function isEmail(s) { return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(s || ""); }
function pageHtml(title, body) {
  return new Response(
    `<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
     <title>${title}</title></head><body style="margin:0;background:#eef1f5;font-family:-apple-system,Segoe UI,sans-serif">
     <div style="max-width:480px;margin:8vh auto;background:#fff;border-radius:16px;padding:32px 28px;text-align:center;box-shadow:0 8px 30px rgba(16,19,26,.08)">
     <div style="font:800 22px -apple-system,Segoe UI,sans-serif;color:#10131a;margin-bottom:14px">aban<span style="color:#0b5">news</span></div>
     ${body}</div></body></html>`,
    { status: 200, headers: { "Content-Type": "text/html; charset=utf-8", ...CORS } });
}

async function hmac(secret, msg) {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(msg));
  return [...new Uint8Array(sig)].map(b => b.toString(16).padStart(2, "0")).join("");
}
async function token(secret, purpose, email) { return (await hmac(secret, `${purpose}:${email.toLowerCase()}`)).slice(0, 24); }
async function refCode(secret, email) { return (await hmac(secret, `refcode:${email.toLowerCase()}`)).slice(0, 10); }

// ----------------------------------------------------------------- Mail (Resend default)
async function sendMail(env, to, subject, html) {
  if (!env.RESEND_API_KEY) return;
  await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { "Authorization": `Bearer ${env.RESEND_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({ from: env.MAIL_FROM || "aban news <onboarding@resend.dev>", to, subject, html }),
  });
}

function confirmMail(link) {
  return `<div style="font-family:-apple-system,Segoe UI,sans-serif;max-width:520px;margin:0 auto">
    <h1 style="font:700 22px Georgia,serif;color:#10131a">Fast geschafft — bitte bestaetigen</h1>
    <p style="color:#3a4150;font-size:15px;line-height:1.6">Du hast dich fuer <b>aban news</b> angemeldet — taeglich KI &amp; Krypto in 5 Minuten. Klicke kurz zur Bestaetigung:</p>
    <p><a href="${link}" style="display:inline-block;background:#0b5;color:#fff;font-weight:700;text-decoration:none;padding:13px 26px;border-radius:8px">Anmeldung bestaetigen</a></p>
    <p style="color:#8a93a3;font-size:12px">Nicht angefordert? Ignoriere diese Mail.</p></div>`;
}
function welcomeMail(shareLink, statusLink, unsub) {
  return `<div style="font-family:-apple-system,Segoe UI,sans-serif;max-width:520px;margin:0 auto">
    <h1 style="font:700 22px Georgia,serif;color:#10131a">Willkommen bei aban news</h1>
    <p style="color:#3a4150;font-size:15px;line-height:1.6">Ab jetzt bekommst du jeden Morgen die wichtigsten KI- &amp; Krypto-News kompakt auf Deutsch — mit Markt-Snapshot und Einordnung. Sonntags zusaetzlich der Pro Deep-Dive.</p>
    <div style="background:#faf7f2;border-radius:12px;padding:16px 18px;margin:14px 0">
      <div style="font:700 13px -apple-system,Segoe UI,sans-serif;color:#8b7355;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">Empfehlen &amp; Pro gratis</div>
      <p style="color:#3a4150;font-size:14px;line-height:1.6;margin:0 0 8px">Teile deinen Link — ab 3 Werbungen schalten wir dir <b>aban Pro</b> frei (10 = 3 Monate, 25 = ein Jahr):</p>
      <p style="margin:0 0 6px"><a href="${shareLink}" style="color:#0b5;font-weight:700">${shareLink}</a></p>
      <p style="margin:0;font-size:13px"><a href="${statusLink}" style="color:#8a93a3">Deinen Empfehlungs-Stand ansehen</a></p>
    </div>
    <p style="color:#9aa3b2;font-size:12px">Jederzeit <a href="${unsub}" style="color:#9aa3b2">abmelden</a>.</p></div>`;
}

// ----------------------------------------------------------------- Routes
async function subscribe(req, env) {
  const { email, ref } = await req.json().catch(() => ({}));
  if (!isEmail(email)) return json({ ok: false, error: "invalid email" }, 400);
  const e = email.toLowerCase();
  const existing = await env.ABAN_SUBS.get(e, "json");
  if (existing && existing.status === "active") return json({ ok: true, status: "already" });
  const t = await token(env.UNSUB_SECRET, "confirm", e);
  await env.ABAN_SUBS.put(e, JSON.stringify({ status: "pending", referred_by: ref || null, ts: Date.now() }));
  const link = `${api(env)}/confirm?e=${encodeURIComponent(e)}&t=${t}`;
  await sendMail(env, e, "Bitte bestaetige deine aban-news-Anmeldung", confirmMail(link));
  return json({ ok: true, status: "pending" });
}

async function confirm(url, env) {
  const e = (url.searchParams.get("e") || "").toLowerCase();
  const t = url.searchParams.get("t") || "";
  if (!isEmail(e) || t !== (await token(env.UNSUB_SECRET, "confirm", e)))
    return pageHtml("Link ungueltig", `<p style="color:#3a4150">Dieser Bestaetigungslink ist ungueltig oder abgelaufen.</p>`);

  const prev = (await env.ABAN_SUBS.get(e, "json")) || {};
  const code = await refCode(env.UNSUB_SECRET, e);
  const rec = { status: "active", edition: prev.edition || "free", referrals: prev.referrals || 0,
                ref_code: code, referred_by: prev.referred_by || null, ts: Date.now() };
  await env.ABAN_SUBS.put(e, JSON.stringify(rec));
  await env.ABAN_SUBS.put("ref:" + code, e);                       // Code -> E-Mail (Lookup)

  if (prev.referred_by && prev.referred_by !== code) await creditReferrer(env, prev.referred_by);

  const ut = await token(env.UNSUB_SECRET, "unsub", e);
  const st = await token(env.UNSUB_SECRET, "status", e);
  const share = `${site(env)}/?ref=${code}`;
  const statusLink = `${api(env)}/status?e=${encodeURIComponent(e)}&t=${st}`;
  await sendMail(env, e, "Willkommen bei aban news", welcomeMail(share, statusLink, `${api(env)}/abmelden?e=${encodeURIComponent(e)}&t=${ut}`));
  return pageHtml("Bestaetigt", `<h2 style="color:#10131a;font-family:Georgia,serif">Anmeldung bestaetigt</h2>
    <p style="color:#3a4150">Willkommen bei aban news. Deine erste Ausgabe kommt morgen frueh.</p>
    <div style="background:#faf7f2;border-radius:12px;padding:16px;margin:16px 0">
      <p style="color:#3a4150;font-size:14px;margin:0 0 8px">Empfiehl aban news weiter und hol dir <b>Pro gratis</b> (ab 3 Werbungen):</p>
      <p style="margin:0"><a href="${share}" style="color:#0b5;font-weight:700">${share}</a></p></div>
    <p><a href="${site(env)}" style="color:#0b5">Zur Startseite</a></p>`);
}

async function creditReferrer(env, code) {
  const refEmail = await env.ABAN_SUBS.get("ref:" + code);
  if (!refEmail) return;
  const r = await env.ABAN_SUBS.get(refEmail, "json");
  if (!r || r.status !== "active") return;
  r.referrals = (r.referrals || 0) + 1;
  const m = MILESTONES.filter(x => r.referrals >= x.n).pop();   // hoechster erreichter Meilenstein
  if (m) {
    r.edition = "pro";
    r.pro_until = Date.now() + m.months * 30 * 24 * 3600 * 1000;
    if (!r.rewarded || r.rewarded < m.n) {
      r.rewarded = m.n;
      await sendMail(env, refEmail, "Du hast aban Pro freigeschaltet!",
        `<div style="font-family:-apple-system,Segoe UI,sans-serif"><h1 style="font:700 22px Georgia,serif;color:#10131a">Geschafft — ${m.months} Monat(e) aban Pro!</h1>
         <p style="color:#3a4150;font-size:15px">Danke fuers Empfehlen. Du hast ${r.referrals} Personen geworben und damit <b>${m.months} Monat(e) aban Pro</b> freigeschaltet. Weiter so!</p></div>`);
    }
  }
  await env.ABAN_SUBS.put(refEmail, JSON.stringify(r));
}

async function status(url, env) {
  const e = (url.searchParams.get("e") || "").toLowerCase();
  const t = url.searchParams.get("t") || "";
  if (!isEmail(e) || t !== (await token(env.UNSUB_SECRET, "status", e)))
    return pageHtml("Link ungueltig", `<p style="color:#3a4150">Dieser Link ist ungueltig.</p>`);
  const r = (await env.ABAN_SUBS.get(e, "json")) || {};
  const n = r.referrals || 0;
  const next = MILESTONES.find(x => n < x.n);
  const share = `${site(env)}/?ref=${r.ref_code || ""}`;
  const prog = next ? `Noch <b>${next.n - n}</b> bis zu ${next.months} Monat(en) Pro.` : "Maximaler Rang erreicht — danke!";
  return pageHtml("Dein Empfehlungs-Stand", `
    <h2 style="color:#10131a;font-family:Georgia,serif">Deine Empfehlungen</h2>
    <div style="font:800 44px Georgia,serif;color:#0b5;margin:8px 0">${n}</div>
    <p style="color:#3a4150">${prog}</p>
    <div style="background:#faf7f2;border-radius:12px;padding:14px;margin:14px 0">
      <div style="font-size:13px;color:#8a93a3;margin-bottom:6px">Dein Link</div>
      <a href="${share}" style="color:#0b5;font-weight:700;word-break:break-all">${share}</a></div>
    ${r.edition === "pro" ? '<p style="color:#0b5;font-weight:700">Status: aban Pro aktiv</p>' : ""}`);
}

async function unsubscribe(url, env) {
  const e = (url.searchParams.get("e") || "").toLowerCase();
  const t = url.searchParams.get("t") || "";
  if (!isEmail(e) || t !== (await token(env.UNSUB_SECRET, "unsub", e)))
    return pageHtml("Link ungueltig", `<p style="color:#3a4150">Dieser Abmelde-Link ist ungueltig.</p>`);
  const r = (await env.ABAN_SUBS.get(e, "json")) || {};
  r.status = "unsubscribed"; r.ts = Date.now();
  await env.ABAN_SUBS.put(e, JSON.stringify(r));
  return pageHtml("Abgemeldet", `<p style="color:#3a4150">Du wurdest abgemeldet. Schade, dass du gehst.</p>`);
}

async function exportCsv(url, env) {
  if ((url.searchParams.get("key") || "") !== env.ADMIN_KEY) return new Response("forbidden", { status: 403 });
  const rows = ["email,edition,status,joined,referrals"];
  let cursor;
  do {
    const list = await env.ABAN_SUBS.list({ cursor });
    for (const k of list.keys) {
      if (k.name.startsWith("ref:")) continue;
      const v = await env.ABAN_SUBS.get(k.name, "json");
      if (v && v.status === "active") {
        const ed = (v.edition === "pro" && (!v.pro_until || v.pro_until > Date.now())) ? "pro" : "free";
        rows.push(`${k.name},${ed},active,${new Date(v.ts || Date.now()).toISOString().slice(0, 10)},${v.referrals || 0}`);
      }
    }
    cursor = list.list_complete ? null : list.cursor;
  } while (cursor);
  return new Response(rows.join("\n"), { headers: { "Content-Type": "text/csv", ...CORS } });
}
