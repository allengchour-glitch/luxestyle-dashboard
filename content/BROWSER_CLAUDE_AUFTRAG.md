# 🤖 AUFTRAG für Browser-Claude — LuxeStyle Auto-Reels + offene Admin-Punkte

> Copy-paste an Browser-Claude (Cloud). Alle Vorlagen liegen im Repo unter `content/`.

**Kontext:** Claude Code hat alles vorbereitet (Repo `allengchour-glitch/luxestyle-dashboard`, branch `main`, Ordner `content/`):
- `reels-schedule-90.csv` (3 Reels/Tag, Mix Herren/Schmuck/US/Tech · Spalten: date,time_cet,platform,product,niche,format,hook,caption,hashtags,code,lang,video_file,link)
- `revid-render-payloads.json` (16 fertige Revid v3 Render-Payloads, Premium-Look)
- `revid-prompts.md`, `revid-api-usage.md`, `makecom-autopost-blueprint.md`, `make-build-recipe.md`

**Brand-Regel:** premium/clean, Fokus aufs Produkt. **KEINE** billig wirkenden Stock-Clips (Massen-Schuhe/Brillen/Kleider, generische Model-Clips). HeyGen-Avatare NICHT für Produkte.

## 1) Revid einrichten
- Auf revid.ai **Growth ($39)** abschließen, **API-Key** holen (Settings/API).
- Test: 1 Reel mit Payload aus `revid-render-payloads.json` (z. B. „Sunset Projection Lamp"), 9:16, quality ultra, `stylePrompt` behalten.
- Video prüfen: premium genug (kein Billig-Stock)? Wenn nein → Prompt/Settings anpassen, neu generieren.

## 2) Make.com-Szenario bauen
Account: Org **7603352** · Team **1667409** · eu1. Connections vorhanden: Shopify, **YouTube**, Gmail, **Buffer**.
Baue exakt nach `content/make-build-recipe.md`:
- **Szenario A „Reel generieren":** Google Sheet (aus `reels-schedule-90.csv`) → HTTP POST Revid render (Header `key: REVID_KEY`, Body = passender Payload) → Sheet-Status „rendering".
- **Szenario B „Posten":** Webhook (Revid fertig) → Video download → **Buffer** Post (TikTok+Instagram+Threads, `caption`+`hashtags`) → **YouTube** Upload (#Shorts, privacy **erst PRIVATE**) → **Discord**-Notify „✅ Live: {product}" → Sheet-Status „posted".
- **Testen:** YouTube private, Buffer als Draft/Queue → 1 Zeile durchlaufen, Qualität prüfen → wenn gut: public + Scheduling 3×/Tag aktivieren.
- Alten **„ABAN Files"-Flow NICHT** verwenden (off-brand).

## 3) Discord
Webhook-URL aus dem Channel in das Discord-Modul (Szenario B) eintragen.

## 4) Weitere offene Punkte
- **TikTok-Anzeige** „LuxeStyle Mode CH – Sommer": Optimierungsereignis **Complete Payment** + 4 Creatives → veröffentlichen.
- **Klaviyo:** 18 Templates („LuxeStyle · …") den Flows zuweisen (Abandoned Cart, Welcome, Post-Purchase, Win-Back) + dyn. Warenkorb-Block → aktivieren.
- **DSers-Mapping** der 6 US-Produkte (via AliExpress Selection Standard):
  Diffuser → $5.16–5.30 · Jewelry → $1.50–1.81 · Phone → $4.94–5.78 (free ship) · Sunset → $6.06 · Clock → $6.27 · Straw → $12.41–13.29.
- **Shopify:** EU-IOSS + UK-VAT (Einstellungen → Steuern) und Multi-Currency (Shopify Payments) prüfen.

## 5) Sicherheit
Alten **Make-API-Key rotieren** (war im Chat exponiert).

> Nach jedem Schritt kurz Status + Screenshot berichten.
