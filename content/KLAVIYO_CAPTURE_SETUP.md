# Klaviyo · E-Mail-Capture herrichten (der Signup-Leak)

**Befund (live geprüft, 2026-06-09):**
- **10 Flows sind bereits LIVE** (Welcome DE+EN, Abandoned Cart, Abandoned Checkout, Win-Back, Post-Purchase, VIP).
  Es muss **nichts** „scharfgeschaltet" werden.
- **Aber: „Email List" = 1 Profil, „Newsletter Subscribers" = 0, Flow-Report (90 T.) = leer.**
- **Auf luxestyle.ch ist KEIN Klaviyo-Onsite-Snippet/Popup aktiv** — nur das Theme-Footer-Feld. → Es wird nichts eingesammelt.
- Gut: Im **Checkout** ist das E-Mail-Opt-in vorab angehakt → Käufer landen in der Liste/Flows.

→ Fazit: Die E-Mail-Maschine ist fertig. Es fehlt **(a) Capture auf der Seite** und **(b) Traffic**.

## A) Klaviyo-Onsite aktivieren (Voraussetzung fürs Popup)
Ohne das Onsite-Snippet kann kein Popup erscheinen.
1. Klaviyo → **Settings → Integrations → Shopify** → sicherstellen, dass **Onsite/Web-Tracking** aktiv ist
   (Klaviyo fügt das Snippet automatisch in den Shop ein).
2. Falls nicht verfügbar: Klaviyo-**Public API Key** (Company ID) holen und das Snippet ins Theme einbauen
   (`<script async src="https://static.klaviyo.com/onsite/js/klaviyo.js?company_id=DEIN_PUBLIC_KEY"></script>`)
   — auf einem **Draft-Theme**, dann veröffentlichen.

## B) Popup erstellen (das #1 Listen-Wachstum)
1. Klaviyo → **Sign-up Forms → Create Form → Popup**, Vorlage „Discount".
2. Anreiz: **10% mit WELCOME10** (Code gilt im Shop). Ein Feld: E-Mail (optional Name).
3. **Ziel-Liste = die, die den Welcome-Flow triggert** (aktuell „Email List" → prüfen, dass „Welcome Series" auf diese Liste hört).
4. Timing: nach ~5–10 s oder bei Exit-Intent. Mobile-Variante aktivieren.
5. **Live schalten** (Publish).

## C) Footer-Feld mappen
Das Theme-Footer-Newsletter-Feld auf dieselbe Liste leiten (Shopify→Klaviyo-Sync), damit auch diese Anmeldungen den Welcome-Flow auslösen.

## D) Aufräumen (niedrige Prio, vor echtem Traffic)
Damit es später kein **Doppel-Mailing** gibt:
- **3 Welcome-Flows** live (`E-Mail Welcome-Serie`, `Welcome Series`, `Welcome Series · EN/US`) → auf **einen** DE-Welcome
  (+ optional EN für US-Markt) reduzieren, Rest pausieren.
- **Abandoned Cart** UND **Abandoned Checkout** beide live (Metric-Trigger) → auf **einen** Warenkorb-Pfad einigen, sonst
  bekommt derselbe Besucher evtl. zwei Mails.
- **„Email List" = Double-Opt-in:** für einen jungen Shop eher **Single-Opt-in** (mehr Adressen) ODER sicherstellen,
  dass die Bestätigungsmail zuverlässig ankommt — sonst bleiben Anmeldungen „unbestätigt" hängen.

## Wirkung
Popup live + Traffic → Anmeldungen → Welcome-Flow (mit WELCOME10) feuert automatisch → erste Conversions.
Ab Bestellungen greifen Abandoned-Cart/Checkout + Post-Purchase + Win-Back von selbst.
