# Auftrag für Browser-Claude — aban news: Worker-Update + Automatik + Landing live

**Kontext:** „aban news" ist ein deutscher KI/Krypto-Newsletter. Backend läuft als Cloudflare Worker auf
`api.abannews.com` (Anmeldung/Double-Opt-in/Referral — funktioniert bereits live). Es fehlen 3 Schritte, die
einen eingeloggten Browser im **Cloudflare-Konto des Users** brauchen (Login: der User macht/ist eingeloggt).
GitHub Actions ist für das Konto gesperrt → deshalb manuell über das Cloudflare-Dashboard.

**Konto/Dienste:** Cloudflare (dash.cloudflare.com), Worker-Name **`aban-subscribe`**, Domain `abannews.com`,
Cloudflare-Pages-Projekt `aban-news`. Mail läuft über Resend (Domain verifiziert).

**Mitgelieferte Dateien (vom User):**
- `aban-worker.js` — der vollständige neue Worker-Code (mit täglicher Automatik)
- `index.html` — die fertige Landingpage (Stripe-Button + CHF 9.90)

---

## Aufgabe 1 — Worker aktualisieren (neue Automatik einsetzen)
1. dash.cloudflare.com → **Workers & Pages** → Worker **`aban-subscribe`** öffnen
2. **Edit code** (bzw. „</> Edit code") öffnen
3. Im Editor **gesamten vorhandenen Code löschen** (Strg/Cmd+A → Entf)
4. **Kompletten Inhalt von `aban-worker.js` einfügen**
5. Oben rechts **Deploy / Save and Deploy** klicken
6. **Verifizieren:** `https://api.abannews.com/` im Browser → muss weiterhin „aban news subscribe service" zeigen
   (Worker erreichbar). Erst nach Deploy ist die neue Version aktiv.

## Aufgabe 2 — Cron-Trigger einschalten (tägliche Automatik)
1. Im Worker `aban-subscribe` → **Settings → Triggers → Cron Triggers** → **Add Cron Trigger**
2. Cron-Ausdruck: **`0 5 * * *`** (= 05:00 UTC = 07:00 Schweiz) → **Add / Save**
3. **Verifizieren:** Der Cron-Trigger erscheint in der Liste.

## Aufgabe 3 — Versand testen (sendet nur an eine Adresse)
1. Diesen Link im Browser öffnen:
   `https://api.abannews.com/digest-test?key=0b4a2d44fb4c88b7c903bb0c805e2d93&to=allengchour@gmail.com`
2. **Erwartung:** JSON wie `{"ok":true,"recipients":1,"sent":1,"items":8}` (NICHT „subscribe service" — das hieße,
   der neue Code ist noch nicht deployt → zurück zu Aufgabe 1).
3. Postfach `allengchour@gmail.com` prüfen (auch Spam) → die Test-Ausgabe sollte ankommen.

## Aufgabe 4 — Landingpage live stellen (Direct Upload, ohne GitHub)
1. dash.cloudflare.com → **Workers & Pages** → **Create** → Reiter **Pages** → **Upload assets**
2. Projektname **`aban`** → **Create project**
3. Die Datei **`index.html`** hochladen/reinziehen → **Deploy site**
4. **Verifizieren:** die erzeugte URL (z.B. `https://aban.pages.dev`) öffnen → Landing lädt, Button **„aban Pro werden"**
   führt zu `buy.stripe.com/6oUdRbfKKcfq03ZbaR5wI05`, Preis zeigt **CHF 9.90**, Anmeldeformular vorhanden.
5. Test-Anmeldung mit einer E-Mail → Bestätigungsmail muss kommen (Double-Opt-in).

## Aufgabe 5 (optional) — Pro-Redirect auf der Hauptdomain
Falls `abannews.com/pro` irgendwo verlinkt ist: Cloudflare → `abannews.com` → **Rules → Redirect Rules** →
Create rule → When URI Path **equals** `/pro` → Then **302** → `https://buy.stripe.com/6oUdRbfKKcfq03ZbaR5wI05` → Deploy.

---

## Wichtige Hinweise
- **Keine Secrets/Tokens irgendwo posten** oder in Screenshots zeigen. Der `ADMIN_KEY` im Test-Link (`0b4a2d44…`)
  ist absichtlich nur für den Versand-Test; danach kann der User ihn rotieren.
- Falls in Aufgabe 3 „subscribe service" statt JSON kommt → Worker-Deploy (Aufgabe 1) wurde nicht gespeichert/deployt.
- Nach Abschluss kurz zurückmelden: Worker deployt? Cron gesetzt? Test-Mail angekommen? Landing-URL?

## Was bereits erledigt ist (nicht nötig)
Worker-Grundfunktion live, Resend-Domain verifiziert, Stripe-Produkt „aban Pro" 9,90 CHF + Payment Link,
UNSUB_SECRET/ADMIN_KEY/RESEND_API_KEY/MAIL_FROM als Worker-Secrets gesetzt, erster Abonnent aktiv.
