# aban news Pro — Deploy-Anleitung (Schritt für Schritt)

Ziel: aus dem fertigen Code ein **laufendes, Geld verdienendes** Newsletter-System machen.
Alle Schritte sind Klick-Arbeit (kein Code). Reihenfolge einhalten — jeder Schritt baut auf dem vorigen auf.
Zeitaufwand: ~60–90 Minuten einmalig.

**Ein Wert zieht sich durch alles: `UNSUB_SECRET`.** Wähle ihn einmal (z.B. 30 zufällige Zeichen) und
trage **exakt denselben** überall ein (Cloudflare-Worker + GitHub-Secrets). Sonst passen die Links nicht.

---

## Schritt 1 — Mail-Versand: Resend-Konto (10 Min)
Du brauchst einen Dienst, der die Mails verschickt. Resend hat einen Gratis-Tarif (3 000 Mails/Monat).

1. `resend.com` → Konto anlegen.
2. **Domain verifizieren:** Resend → Domains → `abannews.com` hinzufügen → die angezeigten DNS-Einträge
   (SPF/DKIM) bei deinem DNS (Cloudflare) eintragen. Wichtig für Zustellbarkeit (sonst Spam).
3. Resend → API Keys → **Key erstellen** → kopieren = `RESEND_API_KEY` (gleich gebraucht).
4. Absender festlegen: `MAIL_FROM = "aban news <news@abannews.com>"`.

> Alternative: Brevo/Mailjet (SMTP). Dann im Worker `sendMail` durch `sendBrevo` ersetzen (Kommentar im Code).

---

## Schritt 2 — Cloudflare Worker (das Herzstück, 20 Min)
Der Worker nimmt Anmeldungen, macht Double-Opt-in, verschickt Bestätigung/Welcome und führt den Referral-Loop.

1. Cloudflare-Dashboard → **Workers & Pages** → **Create** → **Worker** → Namen geben (z.B. `aban-subscribe`) → Deploy.
2. **Edit code** → kompletten Inhalt von `content/aban/aban-cloudflare-worker.js` einfügen → **Deploy**.
3. **KV anlegen:** Workers & Pages → **KV** → Create namespace `ABAN_SUBS`.
   Dann zum Worker → **Settings → Variables → KV Namespace Bindings** → Variable `ABAN_SUBS` = der Namespace.
4. **Variablen/Secrets** (Settings → Variables): als *Secret* eintragen:
   - `UNSUB_SECRET` = dein gewähltes Geheimnis
   - `RESEND_API_KEY` = aus Schritt 1
   - `MAIL_FROM` = `aban news <news@abannews.com>`
   - `ADMIN_KEY` = ein zweites Geheimnis (für den Listen-Export)
   - optional `SITE` = `https://abannews.com`
5. **Eigene API-Subdomain** (verhindert Konflikt mit der Hauptseite, die `/subscribe` per 301 abfängt):
   - DNS → Eintrag `api` anlegen: Typ `AAAA`, Name `api`, Inhalt `100::`, **Proxied (orange Wolke)**.
   - Worker → Settings → **Triggers → Routes** → **eine** Route: `api.abannews.com/*` (Zone `abannews.com`).
   - Variable hinzufügen: `API_BASE = https://api.abannews.com`.

**Test:** `https://api.abannews.com/subscribe` (GET) → „aban news subscribe service".
Die Endpunkte sind dann `api.abannews.com/subscribe|confirm|status|abmelden|export`.

---

## Schritt 3 — Landingpage online (10 Min)
1. `content/aban/landing/index.html` nehmen.
2. Cloudflare → **Workers & Pages → Create → Pages** → direkt-Upload ODER mit dem Repo verbinden.
   (Schnell: die eine HTML-Datei als `index.html` hochladen.)
3. Domain zuweisen: `abannews.com` (oder `www`) auf das Pages-Projekt zeigen lassen.
4. In `landing/index.html` ist `ENDPOINT = "https://abannews.com/subscribe"` schon gesetzt — passt zum Worker.

**Test:** Landing öffnen → E-Mail eintragen → du bekommst die Bestätigungsmail → klicken → Welcome-Mail
mit deinem Referral-Link kommt. Wenn das klappt, läuft die ganze Anmelde-Maschine.

---

## Schritt 4 — Stripe für Pro-Einnahmen (10 Min)
1. `stripe.com` → Konto.
2. **Produkt** „aban Pro" → wiederkehrender Preis, z.B. CHF 5/Monat.
3. **Payment Link** erstellen → URL kopieren.
4. Diese URL als `ABAN_PRO_URL` setzen:
   - im GitHub-Secret (Schritt 5) und
   - in `landing/index.html` beim Button `id="pro-link"` (statt `https://abannews.com/pro`).
5. **Pro-Kunden in die Liste:** Stripe → Customers exportieren → die zahlenden Mails in `subscribers.csv`
   mit `edition=pro` übernehmen (oder den Referral-Loop machen lassen). Daran arbeiten wir später ggf. automatisiert.

---

## Schritt 5 — Tägliche Automatik scharf schalten (GitHub Secrets, 10 Min)
Der Workflow `aban-news.yml` baut täglich + versendet. Repo → **Settings → Secrets and variables → Actions → New secret**:

| Secret | Wert |
|---|---|
| `ANTHROPIC_API_KEY` | Key von `console.anthropic.com` → echte Redaktionsqualität statt Heuristik |
| `UNSUB_SECRET` | **gleich wie im Worker** |
| `SMTP_HOST/PORT/USER/PASS` | von Resend (SMTP) oder Brevo |
| `MAIL_FROM` | `news@abannews.com` |
| `ABAN_PRO_URL` | Stripe Payment Link |
| `ABAN_SUBSCRIBERS` | optional: ganze CSV-Liste (sonst zieht der Worker-Export `/export`) |

Manuell testen: Repo → **Actions → aban news — Daily Digest → Run workflow** (Input `send=false` zum Trockenlauf).

---

## Schritt 6 — Affiliate-Links eintragen (5 Min, bringt sofort Geld)
1. `content/aban/partners.sample.json` → kopieren nach `partners.json`.
2. Bei je einem KI- und Krypto-Partner anmelden (Affiliate-Programm) und die **echten** Links eintragen
   (z.B. Krypto-Börse, Hardware-Wallet, KI-Tool, Online-Kurs).
3. `partners.json` liegt lokal/als Secret — die Anzeige erscheint dann automatisch in jeder Ausgabe.

---

## Reihenfolge der Wirkung
1–3 = **Anmeldungen laufen** (ohne das verdienst du nichts). 6 = **erste Einnahmen** schon bei kleiner Liste.
4 = **Pro-Umsatz** ab Reichweite. 5 = **läuft von selbst**. Referral-Loop (schon im Worker) = **Wachstum**.

## Danach: Reichweite holen
- Landing-Link überall teilen (Bio, WhatsApp, Social).
- Jede Ausgabe landet im Archiv (`/archiv/`) → über Zeit Google-Traffic.
- Bestehende Abonnenten werben über ihren Referral-Link (Pro gratis als Anreiz).

## Häufige Fehler
- **Mails landen im Spam** → SPF/DKIM in Schritt 1 nicht gesetzt. Unbedingt verifizieren.
- **Confirm-Link „ungültig"** → `UNSUB_SECRET` im Worker ≠ in den GitHub-Secrets. Müssen identisch sein.
- **Worker-Route greift nicht** → abannews.com muss als Cloudflare-Zone aktiv sein; Route exakt auf den Pfad.
