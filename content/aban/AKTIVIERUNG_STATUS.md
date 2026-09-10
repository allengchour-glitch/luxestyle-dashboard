# aban news Pro — Aktivierungs-Status (Stand 2026-06-12)

## LIVE & END-TO-END BEWIESEN
- **Worker `api.abannews.com` deployt und laeuft** (GitHub Action `aban-worker-deploy.yml`, Repo public).
- **Resend-Domain `abannews.com` verifiziert** -> Mailversand aktiv (`/subscribe` liefert `mail:{ok:true}`).
- **Voller Double-Opt-in getestet:** Anmeldung -> Bestaetigungsmail -> Klick -> aktiv -> Welcome-Mail mit Referral-Link.
- **Erster aktiver Abonnent bestaetigt** (Export: `allengchour@gmail.com,free,active`).
- **Landing LIVE:** https://aban-news.pages.dev (Cloudflare Pages, via `aban-landing-deploy.yml`),
  Formular -> `api.abannews.com/subscribe`, Honeypot aktiv. Eigene Domain optional im Pages-Projekt zuweisen.
- **Worker gehaertet:** Honeypot, E-Mail-Laengenlimit, ref-Cap, idempotentes /confirm, Anti-Bombing (1 Mail/60s je Adresse).
- Endpunkte geprueft: `/subscribe`, `/confirm`, `/status`, `/export`, KV + Custom Domain + Zertifikat.

## OFFEN — naechste Schritte (optional, fuer vollen Betrieb)
1. **Taegliche Newsletter-Automatik** (`aban-news.yml`) scharf schalten — GitHub-Actions-Secrets:
   `SMTP_HOST=smtp.resend.com`, `SMTP_PORT=465`, `SMTP_USER=resend`, `SMTP_PASS=<Resend-Key>`,
   `MAIL_FROM`, `UNSUB_SECRET` (gleich wie Worker), optional `ANTHROPIC_API_KEY`, `ABAN_PRO_URL`.
2. **Stripe Payment Link** „aban Pro" -> `ABAN_PRO_URL` (Pro-Einnahmen).
3. **Affiliate-Links** in `partners.json` (Vorlage `partners.sample.json`).
4. **Bio/Links** auf `https://aban-news.pages.dev` setzen + teilen -> erste echte Anmeldungen.

## Erledigt
- Repo public (Actions laufen). Worker-Secrets (CF-Token/Account, UNSUB_SECRET, ADMIN_KEY, RESEND_API_KEY, MAIL_FROM) gesetzt.
- KV-Deploy robust (erst Namespace suchen, dann anlegen). sendMail mit Status-Rueckgabe (Debug).
- Token-Schema einheitlich (`UNSUB_SECRET` ueberall gleich).

## Re-Deploy
Actions -> „aban — Worker deploy" -> Run workflow (laeuft automatisch durch).
