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
      if (url.pathname === "/digest-test") return digestTest(url, env);   // manueller Test mit ?key=ADMIN_KEY[&to=mail]
      return new Response("aban news subscribe service", { status: 200, headers: CORS });
    } catch (e) {
      return json({ ok: false, error: String(e) }, 500);
    }
  },
  // Taegliche Automatik (Cron-Trigger in Cloudflare einstellen, z.B. "0 5 * * *" = 07:00 CH).
  async scheduled(event, env, ctx) {
    ctx.waitUntil(runDigest(env));
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
  if (!env.RESEND_API_KEY) return { ok: false, reason: "no_resend_key" };
  try {
    const r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { "Authorization": `Bearer ${env.RESEND_API_KEY}`, "Content-Type": "application/json" },
      body: JSON.stringify({ from: env.MAIL_FROM || "aban news <onboarding@resend.dev>", to, subject, html }),
    });
    if (r.ok) return { ok: true };
    let detail = ""; try { detail = (await r.text()).slice(0, 200); } catch (e) {}
    return { ok: false, reason: "http_" + r.status, detail };
  } catch (e) { return { ok: false, reason: "exception", detail: String(e).slice(0, 160) }; }
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
  const body = await req.json().catch(() => ({}));
  const { email, ref, hp } = body;
  if (hp) return json({ ok: true, status: "pending" });             // Honeypot: Bot ausgefuellt -> still ignorieren
  if (!isEmail(email) || String(email).length > 254) return json({ ok: false, error: "invalid email" }, 400);
  const e = email.toLowerCase();
  const existing = await env.ABAN_SUBS.get(e, "json");
  if (existing && existing.status === "active") return json({ ok: true, status: "already" });
  // Anti-Bombing: dieselbe Adresse nicht oefter als 1x/60s erneut anmailen
  if (existing && existing.status === "pending" && existing.ts && (Date.now() - existing.ts) < 60000)
    return json({ ok: true, status: "pending", mailed: false });
  const t = await token(env.UNSUB_SECRET, "confirm", e);
  await env.ABAN_SUBS.put(e, JSON.stringify({ status: "pending", referred_by: (ref ? String(ref).slice(0, 16) : null), ts: Date.now() }));
  const link = `${api(env)}/confirm?e=${encodeURIComponent(e)}&t=${t}`;
  const mail = await sendMail(env, e, "Bitte bestaetige deine aban-news-Anmeldung", confirmMail(link));
  if (!mail.ok) console.log("mail-fail", mail.reason, mail.detail || "");  // Detail nur im Log, nicht in der Antwort
  return json({ ok: true, status: "pending", mailed: mail.ok });
}

async function confirm(url, env) {
  const e = (url.searchParams.get("e") || "").toLowerCase();
  const t = url.searchParams.get("t") || "";
  if (!isEmail(e) || t !== (await token(env.UNSUB_SECRET, "confirm", e)))
    return pageHtml("Link ungueltig", `<p style="color:#3a4150">Dieser Bestaetigungslink ist ungueltig oder abgelaufen.</p>`);

  const prev = (await env.ABAN_SUBS.get(e, "json")) || {};
  if (prev.status === "active") {                                  // idempotent: nicht erneut Welcome senden
    return pageHtml("Schon bestaetigt", `<h2 style="color:#10131a;font-family:Georgia,serif">Schon angemeldet</h2>
      <p style="color:#3a4150">Du bist bereits bestaetigt — danke!</p><p><a href="${site(env)}" style="color:#0b5">Zur Startseite</a></p>`);
  }
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

// ============================================================================
// Taegliche Newsletter-Automatik (Cron) — generiert + versendet auf Cloudflare,
// ganz ohne GitHub/GitLab. Quellen = deutsche KI/Krypto-Feeds (gute Beschreibungen).
// ============================================================================
const DIGEST_FEEDS = [
  { name: "The Decoder", url: "https://the-decoder.de/feed/", topic: "KI" },
  { name: "t3n", url: "https://t3n.de/rss.xml", topic: "KI" },
  { name: "heise", url: "https://www.heise.de/rss/heise-atom.xml", topic: "KI" },
  { name: "BTC-ECHO", url: "https://www.btc-echo.de/feed/", topic: "Krypto" },
  { name: "Blocktrainer", url: "https://www.blocktrainer.de/feed/", topic: "Krypto" },
  { name: "Cointelegraph", url: "https://cointelegraph.com/rss", topic: "Krypto" },
];

function deEntities(s) {
  return (s || "")
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1")
    .replace(/<[^>]+>/g, " ")
    .replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"').replace(/&#0?39;|&apos;/g, "'").replace(/&nbsp;/g, " ")
    .replace(/&#8211;|&#8212;/g, "–").replace(/&[a-z0-9#]+;/gi, " ")
    .replace(/\s+/g, " ").trim();
}
function pick(block, name) {
  const m = block.match(new RegExp(`<${name}[^>]*>([\\s\\S]*?)<\\/${name}>`, "i"));
  return m ? deEntities(m[1]) : "";
}
function pickLink(block) {
  let m = block.match(/<link[^>]*href="([^"]+)"/i);   // Atom
  if (m) return m[1];
  m = block.match(/<link[^>]*>([\s\S]*?)<\/link>/i);   // RSS
  return m ? deEntities(m[1]) : "";
}
async function fetchFeed(f) {
  try {
    const r = await fetch(f.url, { headers: { "User-Agent": "aban-news-worker/1.0" }, cf: { cacheTtl: 300 } });
    if (!r.ok) return [];
    const xml = await r.text();
    const blocks = xml.match(/<item[\s\S]*?<\/item>/gi) || xml.match(/<entry[\s\S]*?<\/entry>/gi) || [];
    return blocks.slice(0, 4).map(b => {
      let sum = pick(b, "description") || pick(b, "summary") || pick(b, "content");
      sum = sum.replace(/Der (Artikel|Beitrag)[\s\S]*$/i, "").replace(/The post[\s\S]*appeared first[\s\S]*$/i, "").trim();
      if (sum.length > 230) sum = sum.slice(0, 227).replace(/\s\S*$/, "") + "…";
      return { title: pick(b, "title"), link: pickLink(b), summary: sum, source: f.name, topic: f.topic };
    }).filter(x => x.title && x.link);
  } catch (e) { return []; }
}
async function marketSnapshot() {
  try {
    const r = await fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=chf&include_24hr_change=true");
    const d = await r.json();
    const f = (c) => { const p = d[c].chf, ch = d[c].chf_24h_change || 0; return `CHF ${p >= 100 ? Math.round(p) : p.toFixed(2)} ${ch >= 0 ? "▲" : "▼"} (${ch >= 0 ? "+" : ""}${ch.toFixed(1)}%)`; };
    return { btc: f("bitcoin"), eth: f("ethereum") };
  } catch (e) { return null; }
}
function digestHtml(items, market, dateStr) {
  const a = "#0b5", dark = "#10131a";
  const esc = (s) => (s || "").replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
  let cur = "", rows = "";
  for (const it of items) {
    if (it.topic !== cur) { cur = it.topic; rows += `<tr><td style="padding:22px 28px 4px"><div style="font:700 12px -apple-system,Segoe UI,sans-serif;letter-spacing:2px;text-transform:uppercase;color:${a}">${esc(cur)}</div></td></tr>`; }
    rows += `<tr><td style="padding:12px 28px;border-bottom:1px solid #e9ecf1">
      <a href="${esc(it.link)}" style="font:700 17px/1.3 Georgia,serif;color:${dark};text-decoration:none">${esc(it.title)}</a>
      <div style="font:600 11px -apple-system,Segoe UI,sans-serif;color:#8a93a3;margin:5px 0 7px;text-transform:uppercase">${esc(it.source)}</div>
      <div style="font:400 14px/1.55 -apple-system,Segoe UI,sans-serif;color:#3a4150">${esc(it.summary)}</div></td></tr>`;
  }
  const mk = market ? `<tr><td style="padding:0 28px 12px"><span style="font:600 12px -apple-system,Segoe UI,sans-serif;color:#8a93a3">Markt:</span> <span style="font:700 13px -apple-system,Segoe UI,sans-serif;color:${dark}">BTC ${esc(market.btc)} · ETH ${esc(market.eth)}</span></td></tr>` : "";
  return `<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
  <body style="margin:0;background:#eef1f5;padding:24px 0">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
  <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 8px 30px rgba(16,19,26,.08)">
  <tr><td style="background:${dark};padding:24px 28px"><div style="font:800 22px -apple-system,Segoe UI,sans-serif;color:#fff">aban<span style="color:${a}">news</span></div>
  <div style="font:400 13px -apple-system,Segoe UI,sans-serif;color:#aeb6c4;margin-top:6px">KI &amp; Krypto · ${dateStr} · in 5 Minuten auf dem Laufenden</div></td></tr>
  ${mk}${rows}
  <tr><td style="padding:20px 28px;background:#fafbfc;text-align:center">
  <a href="https://buy.stripe.com/6oUdRbfKKcfq03ZbaR5wI05" style="display:inline-block;background:${a};color:#fff;font:700 14px -apple-system,Segoe UI,sans-serif;text-decoration:none;padding:11px 22px;border-radius:8px">aban Pro werden</a>
  <div style="font:400 11px -apple-system,Segoe UI,sans-serif;color:#9aa3b2;margin-top:12px">{{UNSUB}}</div></td></tr>
  </table></td></tr></table></body></html>`;
}
async function buildDigest() {
  const all = (await Promise.all(DIGEST_FEEDS.map(fetchFeed))).flat();
  const seen = new Set(), items = [];
  for (const it of all) { const k = it.link.split("?")[0]; if (!seen.has(k)) { seen.add(k); items.push(it); } }
  const ki = items.filter(i => i.topic === "KI").slice(0, 4);
  const kr = items.filter(i => i.topic === "Krypto").slice(0, 4);
  const sel = [...ki, ...kr];
  const market = await marketSnapshot();
  const dateStr = new Date().toLocaleDateString("de-CH", { day: "2-digit", month: "2-digit", year: "numeric" });
  return { html: digestHtml(sel, market, dateStr), count: sel.length, date: dateStr };
}
async function runDigest(env, onlyTo) {
  const { html, count, date } = await buildDigest();
  if (!count) return { ok: false, reason: "no_items" };
  const subject = `aban news · KI & Krypto — ${date}`;
  const recipients = [];
  if (onlyTo) recipients.push(onlyTo);
  else {
    let cursor;
    do {
      const list = await env.ABAN_SUBS.list({ cursor });
      for (const k of list.keys) {
        if (k.name.startsWith("ref:")) continue;
        const v = await env.ABAN_SUBS.get(k.name, "json");
        if (v && v.status === "active") recipients.push(k.name);
      }
      cursor = list.list_complete ? null : list.cursor;
    } while (cursor);
  }
  let sent = 0;
  for (const e of recipients) {
    const ut = await token(env.UNSUB_SECRET, "unsub", e);
    const unsub = `<a href="${api(env)}/abmelden?e=${encodeURIComponent(e)}&t=${ut}" style="color:#9aa3b2">Abmelden</a>`;
    const r = await sendMail(env, e, subject, html.replace("{{UNSUB}}", unsub));
    if (r.ok) sent++;
  }
  return { ok: true, recipients: recipients.length, sent, items: count };
}
async function digestTest(url, env) {
  if ((url.searchParams.get("key") || "") !== env.ADMIN_KEY) return new Response("forbidden", { status: 403 });
  const to = url.searchParams.get("to") || null;   // ?to=mail = nur an diese Adresse (Test), sonst ganze Liste
  const res = await runDigest(env, to);
  return json(res);
}
