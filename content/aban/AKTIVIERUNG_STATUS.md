# aban news Pro — Aktivierungs-Status (Stand 2026-06-12)

## LIVE & getestet
- **Worker `api.abannews.com` ist deployt und laeuft** (via GitHub Action `aban-worker-deploy.yml`, Repo public).
- Endpunkte live geprueft: `/` (200), `/subscribe` (Validierung 400 bei Murks), `/export` (403 ohne Key),
  `/confirm` (lehnt falschen Token ab). KV, Secrets, Custom Domain + Zertifikat aktiv.
- Test-Anmeldung `allengchour@gmail.com` -> `{"ok":true,"status":"pending"}` (Bestaetigungsmail ausgeloest).

## OFFEN — beim naechsten Mal testen/erledigen
1. **Bestaetigungsmail pruefen** (Gmail allengchour@gmail.com, auch Spam):
   - kommt an -> „Anmeldung bestaetigen" tippen -> aktiv + Welcome-Mail mit Referral-Link = **voll live**.
   - kommt NICHT an -> **Resend-Domain verifizieren**: resend.com/domains -> abannews.com -> die 3 DNS-Eintraege
     (SPF/DKIM) bei Cloudflare DNS eintragen -> „Verify". Erst danach liefert Resend an beliebige Adressen.
2. **Landing online stellen** (damit Besucher das Formular sehen): `content/aban/landing/index.html` als
   Cloudflare Pages deployen; Endpoint zeigt schon auf `https://api.abannews.com/subscribe`.
3. **Taegliche Newsletter-Automatik** (`aban-news.yml`) scharf schalten — braucht GitHub-Actions-Secrets:
   `SMTP_HOST=smtp.resend.com`, `SMTP_PORT=465`, `SMTP_USER=resend`, `SMTP_PASS=<Resend-Key>`,
   `MAIL_FROM`, `UNSUB_SECRET` (gleich wie im Worker), optional `ANTHROPIC_API_KEY` (Redaktionsqualitaet),
   `ABAN_PRO_URL` (Stripe).
4. **Stripe Payment Link** „aban Pro" -> `ABAN_PRO_URL` (Pro-Einnahmen).
5. **Affiliate-Links** in `partners.json` (Vorlage `partners.sample.json`) -> verdient ab dem ersten Leser.

## Erledigt
- Repo public (Actions laufen). Secret `RESEND_API_KEY` + die Cloudflare-/Worker-Secrets gesetzt -> Deploy erfolgreich.
- Token-Schema einheitlich (`UNSUB_SECRET` ueberall gleich).

## Re-Deploy bei Aenderungen
Actions -> „aban — Worker deploy" -> Run workflow. Laeuft automatisch durch (KV/Secrets/Deploy).
