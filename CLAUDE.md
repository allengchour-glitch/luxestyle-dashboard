# LuxeStyle Dashboard — Projekt-Memory

Internes Single-Page-Dashboard für den Dropshipping-/Mode-Shop **LuxeStyle**. Statisches
HTML/CSS/JS, kein Build-Step, Deploy über Netlify.

## ⚠️ Offene To-dos / Sicherheit (ZUERST LESEN · Stand 2026-06-02)
- [ ] **TikTok-Access-Token rotieren** — wurde im Chat exponiert (Token + Advertiser-ID `7646349875793182738`). Neuen Token mit Scope **Creative Management** generieren (sonst Upload-Fehler 40001).
- [x] **DSers-Mapping gefixt** (2026-06-03): 18K Gold-Set → echter Lieferant **DIEYURO 316L Set** (Gold=B612, Silver=N1725), Cost ~CHF 1.75–3.95. Anleitung: `content/DSERS_MAPPING_FIX.md`.
- [x] **Counterfeit-/IP-Risiko:** Herren Sommer-Set (POLO), Gym-Shirt (Superman), Tracksuit (Wasserzeichen) **archiviert** (2026-06-03). Restliches Herren-Apparel noch sichten.
- [x] **US/Summer published** (Onlineshop+TikTok, 2026-06-03): Rain Cloud Diffuser · Sunset Lamp · **18K Gold-Set** (nach DSers-Fix) — alle live & kaufbar.
- [ ] **Ohrring-Set-Preis** = CHF 22.90 (nicht 29.90) — in Creatives korrekt halten.
- [ ] TikTok-Kampagne `luxestyle.ch`: Optimierungsereignis **Complete Payment** aktivieren + Creatives veröffentlichen.

## Wichtigste Fakten
- **Eine Datei zählt:** `index.html` enthält praktisch das gesamte Dashboard (HTML + CSS + JS inline).
- **Kein Backend für eigene Daten** → alle benutzerpflegbaren Daten liegen im **`localStorage`** des Browsers.
- **Zwei separate Shops:**
  - `luxestyle.com.co` — Haupt-Shopify-Shop (Pixel `D85BAGJC77UF23S9UDH0`, im Settings-Tab geführt).
  - `luxestyle.ch` — separater Shop für die TikTok-Sommer-Kampagne (eigenes Pixel `D8EQE4JC77UAEKHUJCM0`,
    Snippet in `snippets/tiktok-pixel-luxestyle-ch.html`). Diese beiden NICHT verwechseln.
- **Sprache der UI:** Deutsch (Schweiz). Neue Creator-/Kunden-Texte gibt es oft zusätzlich auf Englisch.

## Dateien
- `index.html` — Dashboard (Tabs, Logik). **Hier passiert fast alles.**
- `netlify/functions/shopify-oauth-callback.js`, `shopify-proxy.js` — Shopify-Anbindung (nur Shopify, nichts Eigenes).
- `netlify.toml` — Build/Headers. `tiktok_videos.json` — Quelle für den Content-Tab (Video-Pipeline).
- `snippets/tiktok-pixel-luxestyle-ch.html` — TikTok-Pixel-Code für den luxestyle.ch-Storefront (NICHT ins Dashboard einbauen).

## Tabs (`index.html`)
`overview` (Cockpit) · `products` (Shop) · `marketing` · `affiliate` · `pipeline` · `launchpad` · `stats` · `content` · `settings`.
Tab-Wechsel über `showTab(event, 'id')`. Für Sprung-Links aus anderen Tabs: `showTab(null, 'id')`.

## Selbstgebaute Module & ihre localStorage-Keys
| Modul | Tab | localStorage-Key | Render-/Init-Funktion |
|---|---|---|---|
| Affiliate-Programm + Creator-Tracking | `affiliate` | `luxe_affiliate_v1` | `affInit` / `affRenderCreators` |
| Kampagnen-To-do (Sommer) | `marketing` | `luxe_campaign_v1` | `campInit` / `campToggleStep` |
| E-Mail-Flow-Setup-Checkliste | `marketing` | `luxe_email_v1` | `emailInit` / `emailToggleStep` |
| Automation-Mails (8×, DE/EN) | `marketing` | `luxe_mail_v1` (+ `luxe_mail_lang_v1`) | `mailRender` |
| TikTok-Kommentar-Antworten (17×, DE/EN) | `content` | `luxe_tt_replies_v1` (+ `luxe_tt_lang_v1`) | `ttReplyRender` |
| Mode-Creatives (8×, DE/EN) | `content` | `luxe_creative_v1` (+ `luxe_creative_lang_v1`) | `creativeRender` |
| Kundenservice-Antworten (DE/EN) | `marketing` | `luxe_service_v1` (+ `luxe_service_lang_v1`) | `serviceRender` |
| Cockpit-Übersicht (aggregiert) | `overview` | — (liest die obigen) | `cockpitRender` |

Alle Render-Funktionen werden am Ende des Haupt-`<script>` initial aufgerufen (Block direkt vor `</script>`).

## Konventionen / Muster
- **Globale Funktionen**, inline `onclick="..."` als Event-Verdrahtung (kein Framework, kein Bundler).
- HTML wird per String-Konkatenation gebaut. Beim Einsetzen von User-/Default-Text in HTML
  `affEsc(text)` zum Escapen nutzen (existiert im Affiliate-Block).
- Bilinguale Module: Daten-Array mit `{ de: ..., en: ... }`, Sprach-Toggle-Buttons mit
  eigenem `data-*lang`-Attribut, Auswahl + Edits getrennt pro Sprache in localStorage.
- Wiederverwendbare CSS-Klassen: `.section`, `.section-header`, `.section-subtitle`, `.section-title`,
  `.kpi-grid`/`.kpi`, `.grid-2`, `.profit-card`/`.profit-row(.total/.profit)`, `.table`,
  `.alert(-info/-success/-warning)`, `.btn`/`.btn-sm`/`.btn-primary`, `.ttf-btn(.ttf-active)`,
  `.tt-reply`, `.aff-input`/`.aff-cell`/`.aff-step`. Neues CSS sparsam, am besten in den bestehenden `<style>`-Block.
- `copyCode(text)` kopiert in die Zwischenablage (mit Alert-Bestätigung) — für alle 📋-Buttons nutzen.
- **Pixel/Tracking-Snippets gehören NICHT in `index.html`** (das ist das interne Admin-Tool, kein Storefront).

## Vor jedem Commit prüfen
JS-Syntax des Haupt-Skriptblocks validieren und Tag-Balance checken:
```bash
python3 - <<'PY'
import re
html = open('index.html', encoding='utf-8').read()
blocks = re.findall(r'<script>(.*?)</script>', html, re.S)
open('/tmp/main.js','w',encoding='utf-8').write(blocks[-1])
print('script blocks:', len(blocks))
PY
node --check /tmp/main.js
python3 -c "h=open('index.html').read(); print('divs:',h.count('<div'),h.count('</div>'))"
```
Erwartung: **3** Script-Blöcke (winziges Head-Theme-Init für Dark-Mode · Content-Tab · Haupt-Skript),
`node --check` ohne Fehler (prüft den letzten/Haupt-Block), `<div>`/`</div>` ausgeglichen.
Funktionaler Test: `index.html` im Browser öffnen — alles läuft client-seitig, Netlify nicht nötig.

## Git / Workflow
- Entwicklungs-Branch: `claude/blissful-albattani-wUQZV`. Push mit `git push -u origin <branch>`.
- **PR #1** (Affiliate · Kampagne · E-Mail-Flows · TikTok-Antworten · Creatives · Cockpit) ist **gemergt** (squash → `main`).
- **PR #2** (Draft) — Kundenservice-Antworten-Modul. Nach dem Push immer einen (Draft-)PR sicherstellen.
- **PR #20** (Ready for review) — Reel-/Ad-Pipeline + finale TikTok-Ad „Sommer 2026" (`content/ads/`, Handoff `BROWSER_CLAUDE_TIKTOK_AD.md`, Manifest/Rezepte in `content/`). Stand 2026-06-02.
- Footer-Versionsstring in `index.html` (Suche `class="footer"`) bei größeren Änderungen mitziehen.

## Externer Projekt-Stand (außerhalb des Repos · Juni 2026)
Läuft über In-Admin-Tools / MCP, NICHT im Dashboard-Code:
- **Shopify** (`luxestyle.ch`, CHF · Markets: **USA = USD aktiv**): 5 Produkte „US/Summer 2026" live mit
  Bild + Varianten + Dropship-Inventar (SKUs `LX-DIFF/LAMP/CLOCK/PHN/JWL`), Collection „US / Summer 2026".
  Echte Dropship-Produkte kommen über **CJ/DSers** (echte Fotos + Lieferanten-SKUs, z. B. Ring, Shorts).
- **Klaviyo** (Account = LuxeStyle CH, hängt am `.com.co`-Shop): **14 E-Mail-Templates** (7 DE + 7 EN:
  Cart 1–3, Welcome 1–2, Post-Purchase, Win-Back), Branding Taupe/Cream, Code `WELCOME10`.
  Flows müssen in der Klaviyo-UI gebaut/aktiviert werden (API kann keine Flow-Trigger anlegen).
- **Loox:** 56 Reviews (5.0★) importiert, Core-Script im Theme aktiv.
- **TikTok Ads** (`luxestyle.ch`): Kampagne „LuxeStyle Mode CH – Sommer" als Entwurf; Pixel
  `D8EQE4JC77UAEKHUJCM0` aktiv. Offen: Optimierungsereignis **Complete Payment** + 4 Creatives → veröffentlichen.
- **Nur In-Admin (keine API für Claude):** DSers, Loox, TikTok/Meta Ads.
- **Bild-Lektion:** Shopify-Produktbilder müssen **< 25 MP** sein, sonst Fehler „Mediendatei konnte nicht
  verarbeitet werden". Adobe-Stock-**Free**-Collection taugt für Platzhalter (0 Credits, kommerziell nutzbar) —
  große Assets (>25 MP) vorher herunterskalieren (z. B. `image_crop_and_resize`).

## 🎨 Brand-Bildsprache (WICHTIG — User-Vorgabe)
Visuals/Reels: **premium, clean, lifestyle, Fokus aufs Produkt.** **Vermeiden:** billig wirkende Generic-Stock-Clips
(Massen-Schuhe/Brillen/Kleider, generische Model-Stockclips) — alles, was nach Billig-Dropshipping aussieht.
Hochwertige, ästhetische Optik. (In `content/revid-render-payloads.json` als `stylePrompt` + `quality:ultra` hinterlegt.)

## 🎬 Content-/Reel-Automation (`content/`)
- `reels-schedule.csv` (14T) · `-30d.csv` · `-90.csv` (3×/Tag, Mix Herren/Schmuck/US/Tech) · `reel-posting-plan*.md`
- `revid-prompts.md` (Script-Prompts je Produkt) · `revid-render-payloads.json` (16 fertige v3-render-Payloads, Premium-Settings)
- `revid-api-usage.md` · `makecom-autopost-blueprint.md`
- `tools/build_reel.py` (v3) — **Automatisierungs-Tool**: JSON/CLI → fertiges TikTok-Premium-9:16-Reel/Ad. Features: **Shopify-Auto-Modus** (`--shopify handles` / `--shopify-query 'tag:..'` → zieht Titel/Preis/Bild per Admin-API, ENV `SHOPIFY_STORE`+`SHOPIFY_ADMIN_TOKEN`, überspringt nicht-published), **A/B-Hooks** (mehrere Varianten → `_A/_B`), Hook-/Social-Proof-Karten, animierte Captions, Story-Progress-Bar, Preis-Badge, Musik-Moods, Markenfarbe. Cross-platform. Doku: `tools/README.md`.
- `tools/tiktok_upload.py` — lädt fertige Reels per **TikTok Marketing API** in den Ads Manager (Creative Library). ENV `TIKTOK_ACCESS_TOKEN`+`TIKTOK_ADVERTISER_ID`. `python tiktok_upload.py reel.mp4` (oder `--url`, `--list`). Pipeline: build_reel.py → tiktok_upload.py. `tools/get_token.py` holt den Access-Token (OAuth auth_code→token; braucht App-Scope **Creative Management**, sonst Fehler 40001).
- `shopify-product-videos.json` (17 echte Shop-Videos: 13 Produkt-Demos + 4 fertige 9:16-Ads, per Admin-API gefunden) · `revid-custom-media-recipe.md` (echte Fotos/Videos statt Stock via `media.type:custom`) · `reel-build-recipe-ffmpeg.md` (lokale 9:16-Montage; ffmpeg-Build **ohne drawtext** → Text als PNG-Overlay) · `reels-produced-2026-06.md` (Log)
- **Reel-Learnings (2026-06):** Für **produkttreue** Reels echte Shop-Assets nutzen (Stock = nur Lookalike). Flüssiger Ken-Burns = Standbild in 2×-Auflösung + linearer `zoompan` (kein `setpts`-Slow-Mo → ruckelt). Manche Demo-Clips zeigen Fremdmarken/Lieferantentexte → croppen. Ad-Kleider («Savanna», «Brise» …) sind KI-Ad-Konzepte → erst als echtes Produkt bestätigen.
- **Revid.ai:** Plan Growth ($39, 2 000 Credits). API `POST https://www.revid.ai/api/public/v3/render` (Header `key` oder `Bearer`), MCP `https://www.revid.ai/api/mcp`. Egress aus Sandbox funktioniert. **API-Key nötig** (im Revid-Konto erstellen). Generieren kostet Credits → klein starten.
- **Make.com:** Org 7603352 · Team 1667409 · Zone **eu1** (Verbindung flaky → Retries). Connections vorhanden: **Shopify, YouTube, Gmail, Buffer**. **Buffer** = Multi-Plattform-Posting (TikTok/IG/Threads/YT). API-Token authentifiziert, aber **OAuth-Connections + Szenario-Aufbau gehören in die Make-UI** (Browser-Claude). API-Key war im Chat exponiert → rotieren.
