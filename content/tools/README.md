# 🤖 LuxeStyle Reel-/Ad-Builder (`build_reel.py`)

Automatisierungs-Tool: macht aus einer **JSON-Konfig** automatisch ein fertiges,
gebrandetes **9:16-Reel/Ad** (TikTok/IG/YT-ready). Kapselt die Pipeline aus
`../reel-build-recipe-ffmpeg.md`.

## Was es automatisch macht
- Lädt Bilder/Videos (lokaler Pfad **oder** http(s)-URL, z.B. Shopify-CDN).
- Normalisiert alles auf **1080×1920** mit **Blur-Fill-Hintergrund** (egal ob quer/quadrat/hoch).
- Legt **LUXESTYLE-Branding + Caption** (Name + Preis) in der **TikTok-Safe-Zone** drüber.
- **Flüssiger, jitterfreier Ken-Burns-Zoom** (Standbild in 2×-Auflösung, linearer Zoom; alternierend rein/raus).
- **Abwechselnde Transitions** (fade / slide) + lizenzfreier **Musik-Bed** + **CTA-End-Card**.
- Export: H.264, **yuv420p**, `+faststart`.

## Installation
```bash
pip install Pillow imageio-ffmpeg
```

## Nutzung
```bash
python3 build_reel.py sample_reel.json
python3 build_reel.py sample_reel.json --out sommer_ad.mp4
```



## Windows-Schnellstart (PowerShell)
Die Datei liegt **im Repo**, nicht in `C:\Users\...`. Erst Repo holen, dann im Tool-Ordner ausführen:
```powershell
pip install Pillow imageio-ffmpeg
git clone https://github.com/allengchour-glitch/luxestyle-dashboard.git
cd luxestyle-dashboard
git checkout claude/blissful-albattani-wUQZV
cd content\tools
python build_reel.py sample_reel.json --out sommer_ad.mp4
```
- Auf Windows meist `python` statt `python3`.
- ffmpeg kommt automatisch über `imageio-ffmpeg` (kein separater Download nötig).
- Font wird automatisch gefunden (Arial/Segoe). Sonst: `set LUXE_FONT=C:\Windows\Fonts\arialbd.ttf`.

## Shopify-Auto-Modus (kein Manifest nötig)
Statt jedes Bild/Preis von Hand: **nur Handles oder einen Filter** angeben – das Tool zieht
**Titel, Preis & Bild selbst per Admin-API**.

**ENV setzen** (Token NICHT committen):
```bash
# Linux/macOS
export SHOPIFY_STORE=xxxx.myshopify.com
export SHOPIFY_ADMIN_TOKEN=shpat_xxx
# Windows
set SHOPIFY_STORE=xxxx.myshopify.com
set SHOPIFY_ADMIN_TOKEN=shpat_xxx
```
**CLI:**
```bash
python build_reel.py --shopify handle1,handle2,handle3 --out reel.mp4
python build_reel.py --shopify-query "tag:sommer-2026 AND status:active" --limit 6
python build_reel.py sample_shopify_auto.json
```
**Filter (`shopify.query`)** = native Shopify-Suchsyntax, u.a.:
`tag:sommer-2026` · `product_type:Damen-Kleid` · `vendor:LuxeStyle` · `status:active` ·
`price:<=30` · `title:Kleid` · Kombi mit `AND`/`OR`/`NOT`.
**Weitere `shopify`-Optionen:** `limit`, `sort` (created/price/title/best), `reverse`,
`only_published` (überspringt nicht gelistete automatisch), `img` (Bildindex),
`price_format` (`"{cur} {price}"`), `default_dur`, `exclude` (Handles), `handles` (statt query).
Nicht-published Produkte werden **automatisch übersprungen** (kein „nicht kaufbar" in der Ad).

## A/B-Hooks (mehrere Varianten für Ad-Tests)
`hooks` als Liste → das Tool baut den Body **einmal** und erzeugt pro Hook eine Datei
(`out_A.mp4`, `out_B.mp4`, …). Hook als Objekt `{title,sub,dur,src}` oder Kurzform `"Titel|Sub"`.
```json
"hooks": [
  {"title":"SOMMER-SALE","sub":"-10% WELCOME10"},
  {"title":"NEU: SOMMER-DROP","sub":"ab CHF 22.90"}
]
```

## TikTok-Premium-Features (v2)
Optionale Top-Level-Keys im Manifest:
| Key | Wirkung |
|---|---|
| `hook` | `{src,title,sub,dur}` – Auto-Opener: grosser Hook-Text über einem Produktbild (Sek.1, stark fürs Halten der Zuschauer) |
| `socialproof` | `{stars,title,sub,foot,dur}` – Karte mit gezeichneten ★-Sternen (vor der End-Card) |
| `progress_bar` | `true`/`false` – Story-Fortschrittsbalken oben (Default an, wenn ffmpeg `drawbox` kann) |
| `price_badge` | `true`/`false` – Preis als gold gefüllte Pille statt schlichtem Text |
| `accent` | Markenfarbe als Hex (z.B. `#C9A24B`) – färbt Linien/Badge/Progress/Sterne |
| `music` | `"upbeat"` (hell, pulsierend) · `"calm"` (ruhiger Pad) · `false` (stumm) |
| `transition` | Crossfade-Dauer s (Default 0.3); Transitions wechseln automatisch (fade/slide/dissolve) |
| `endcard_dur` | Länge der CTA-End-Card |

Captions blenden automatisch animiert ein (Fade). Reihenfolge: **Hook → Items → Social-Proof → End-Card**.

## Voiceover (gratis, lokal — piper-tts)
Optionaler **deutscher Sprecher** ohne API/Cloud, direkt unter die Musik gemischt (Musik wird
automatisch geduckt: Stimme 1.0 / Musik 0.4). Lokal über **piper-tts**, kein Account, keine Credits.

| Key | Wirkung |
|---|---|
| `voiceover` | Sprechertext (DE). Wird synthetisiert und über das Video gelegt. |
| `voice_model` | Optional: Pfad zur `.onnx`-Stimme. Sonst `LUXE_PIPER_VOICE` oder erste `*.onnx` im Tool-Ordner/`/tmp/piper_voice`/CWD. |

**Setup:**
```bash
pip install piper-tts
# eine deutsche Stimme laden (huggingface rhasspy/piper-voices), z.B.:
#   de_DE-thorsten-medium.onnx (+ .onnx.json) nach ./ oder /tmp/piper_voice legen
export LUXE_PIPER_VOICE=/pfad/de_DE-thorsten-medium.onnx   # Windows: $env:LUXE_PIPER_VOICE="..."
```
Fehlt piper oder die Stimme, wird der Voiceover **sauber übersprungen** (Reel baut trotzdem, nur Musik).

## Manifest-Felder (siehe `sample_reel.json`)
| Feld | Bedeutung |
|---|---|
| `brand` / `code` / `domain` | Branding, Rabattcode, Shop-URL (End-Card) |
| `music` | `true`/`false` – lizenzfreier Musik-Bed |
| `transition` | Crossfade-Dauer in s (Default 0.3) |
| `endcard_dur` | Länge der CTA-End-Card (Default 2.6) |
| `out` | Output-Datei (per `--out` überschreibbar) |
| `items[]` | Liste der Segmente (in Reihenfolge) |
| `items[].src` | Bild/Video: lokaler Pfad **oder** URL |
| `items[].type` | `"video"` für Clips (sonst Bild). Video braucht `ss` (Startsekunde) |
| `items[].title` / `sub` | Caption Zeile 1 / Zeile 2 (Preis hier rein) |
| `items[].dur` | Anzeigedauer in s (Default 1.8) |
| `items[].zoom` | `"in"` oder `"out"` (Ken-Burns-Richtung) |
| `items[].fgw` | Vordergrund-Breite px @2× (Default 1720; kleiner = mehr Rand) |

## Bild-URLs & Preise holen
Über die **Shopify-Admin-API** (GraphQL `media`/`priceRangeV2`), siehe
`../shopify-product-videos.json` und `../revid-custom-media-recipe.md`.

## ⚠️ Wichtig (Ad-Compliance)
- Nur **echte, published Produkte** mit **korrektem Preis** bewerben (vorher per API verifizieren).
- **Keine Fremdmarken-Logos** im Bild/Clip (Markenrecht).
- Reviews-/Claim-Angaben müssen stimmen.
- Bezahlte TikTok-Ads: keine Trending-Pop-Songs (nur Commercial Music Library / eigener Bed).

---

# 📤 TikTok-Ad-Upload (`tiktok_upload.py`)

Lädt ein fertiges Reel/Video (z.B. aus `build_reel.py`) in den **TikTok Ads Manager**
(Creative Library des Werbekontos) per **TikTok Marketing API** — nur Standardbibliothek.

**ENV (nichts committen):**
```bash
export TIKTOK_ACCESS_TOKEN=...      # genehmigte TikTok-for-Business-App
export TIKTOK_ADVERTISER_ID=...     # Werbekonto-ID
```
**Nutzung:**
```bash
python tiktok_upload.py reel.mp4 --name "LuxeStyle Sommer A"   # lokale Datei
python tiktok_upload.py --url https://cdn.../reel.mp4 --name "Sommer B"
python tiktok_upload.py reel.mp4 --cover cover.jpg             # + Cover-Bild
python tiktok_upload.py --list                                # Videos im Konto
```
Gibt die **video_id** zurück → danach im Ads Manager als Ad-Creative wählen (oder via
Campaign-/AdGroup-/Ad-Endpoints schalten). Pixel `D8EQE4JC77UAEKHUJCM0`, Optimierung *Complete Payment*.

**End-to-End:** `build_reel.py … --out reel.mp4`  →  `tiktok_upload.py reel.mp4`.

> Token/Advertiser-ID müssen einmalig im TikTok-Developer-/Business-Portal (Browser) erstellt
> bzw. die App genehmigt werden. A/B: `build_reel` erzeugt `_A/_B` → beide hochladen, im Ads Manager gegeneinander testen.


---

# 🔑 TikTok Access-Token holen (`get_token.py`)

Tauscht **app_id + secret + auth_code** gegen einen **access_token** (TikTok Marketing API OAuth)
und zeigt die **advertiser_ids** + Scopes. Interaktiv (Secret-Eingabe unsichtbar):
```bash
python get_token.py            # fragt App ID, Secret, auth_code ab
python get_token.py --app-id 123 --secret abc --auth-code xyz
```
**Voraussetzung (Browser, einmalig):** business-api.tiktok.com/portal → deine App → Scopes
**Ad Account Management** + **Creative Management** aktivieren → App **autorisieren** →
in der Redirect-URL steht `?auth_code=XXXX` (nur ~10 Min gültig).

**Scope-Hinweis:** Der Upload-Endpoint `/file/video/ad/upload/` braucht den Scope
**Creative Management**. Fehlt er → Fehler `40001` (Token neu mit diesem Scope generieren).

---

# 📊 TikTok-Analyse (`tiktok_analyze.py`)

Zieht **öffentliche** Engagement-Daten eines TikTok-Profils (Default `@luxestyle.ch`) — **ohne
API-Key, ohne Login** — via `yt-dlp` und schreibt JSON + Markdown-Report: Views/Likes/Comments,
Ø Engagement-Rate, **Top-Videos**, **Hashtag-Performance**, **beste Posting-Zeiten** (Wochentag/Stunde)
und **Hook-Ranking** (Caption-Anfang). Damit sieht man, was zieht → Input für die nächsten Reels
(`build_reel.py`-Hooks) und den Posting-Plan (`../reels-schedule.csv`).

> Portiert aus dem Schwester-Repo **aban-news-landing** (`tools/tiktok_analyze.py`), Default auf
> `@luxestyle.ch` angepasst.

**Setup:** `pip install -U yt-dlp`

**Nutzung:**
```bash
python tiktok_analyze.py                       # @luxestyle.ch, 30 neueste
python tiktok_analyze.py --user @anderer.shop  # Konkurrenz-Analyse
python tiktok_analyze.py --max 60 --out reports/
# Falls "Unable to extract secondary user ID": eine Video-URL als Seed mitgeben
python tiktok_analyze.py --seed-video https://www.tiktok.com/@luxestyle.ch/video/XXXX
```
Output: `reports/tiktok_luxestyle.ch_<datum>.json` + `.md`. Bricht der TikTok-Extractor → `pip install -U yt-dlp`.

---

# 📣 Posten (`social_post.py`)

Postet ein **Reel** (oder Text+Link) **gratis** auf Telegram & Co. — kein Make/Zapier, nur
Standardbibliothek. Mit `--video` wird das Reel **selbst** hochgeladen (Telegram `sendVideo` /
Discord File-Upload), sonst nur Caption + Shop-Link.

> Portiert/erweitert aus aban-news `social/post.py` (dort nur Text) → hier mit Video-Upload + LuxeStyle-Default-Caption.

**Kanäle** (je per ENV-Secret aktiviert; nicht gesetzt = übersprungen — **nichts in den Chat schreiben!**):
| ENV | Kanal |
|---|---|
| `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` | Telegram (Kanal `@name` oder numerische ID) |
| `DISCORD_WEBHOOK_URL` | Discord |
| `PUBLISH_WEBHOOK_URL` | generischer Webhook → Make/n8n/Zapier → IG/X/LinkedIn |

**Telegram-Setup (einmalig):** @BotFather → `/newbot` → Token = `TELEGRAM_BOT_TOKEN`; Bot als Admin in
den Kanal; Kanalname `@meinkanal` (oder numerische ID) = `TELEGRAM_CHAT_ID`.

**Nutzung:**
```bash
export TELEGRAM_BOT_TOKEN=123456:ABC...   # Windows: $env:TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID=@luxestyle
python social_post.py --video ../ads/LuxeStyle_EU_Hero_Reel.mp4          # Reel + Default-Caption
python social_post.py --text "Sommer-Drop ✨" --link https://luxestyle.ch # eigener Text
python social_post.py --video ../ads/LuxeStyle_Mix_Reel_Sommer.mp4 --dry-run
```
Reels < 50 MB (Telegram-Bot-Limit) — alle `content/ads/*.mp4` liegen drunter.
**Hinweis:** TikTok-Upload/Kommentar bleibt Hand-Arbeit (kein offener Posting-Endpoint).

---

# 🔁 Stunden-Automation (`auto_cycle.py` + GitHub-Action)

Vollautomatischer Loop: **bauen → lernen → Text-Status posten**, ohne dass jede Stunde ein Video in
Telegram landet.

**`product_pool.json`** — kuratierter Pool echter, aktiver, published Produkte (Live aus Shopify, CHF,
quer durch alle Kategorien). Quelle für die Rotation.

**`auto_cycle.py`** — ein Lauf:
1. **Rotiert** einen frischen Mix aus dem Pool (Offset = Stunden seit Epoch → jede Stunde *andere* Gegenstände).
2. **Baut** daraus via `build_reel.py` ein Premium-9:16-Reel (alternierende Musik/Hooks).
3. **Lernt**: liest den neuesten `content/reports/tiktok_*.json` (von `tiktok_analyze.py`) und übernimmt
   Top-Hashtags + bestperformenden Hook in die nächste Caption.
4. **Postet einen Text-Status** (KEIN Video) via `social_post.py` — das Reel-Video bleibt Datei/Artefakt
   für den manuellen TikTok-Upload.
```bash
python auto_cycle.py --count 4 --analyze        # ein Zyklus (mit Analyse)
python auto_cycle.py --no-post --offset 7       # nur bauen, fester Mix (Test)
```

**`.github/workflows/luxestyle-auto.yml`** — `cron: "0 * * * *"` (stündlich) + manuell (`workflow_dispatch`).
Baut das Reel (→ **Artefakt**, nicht ins Repo), committet nur den kleinen Lern-Report/Lauf-Log.
- ⚠️ **Geplante Workflows laufen nur auf dem Default-Branch** → der Stunden-Takt startet erst **nach Merge nach `main`**. Vorher per „Run workflow" testbar.
- Secrets im Repo setzen (NICHT im Chat): `TELEGRAM_BOT_TOKEN` (rotierter Token!) + `TELEGRAM_CHAT_ID`. Ohne Secrets baut der Lauf trotzdem, postet nur nicht.
- Takt entschärfen: cron z.B. auf `"0 */3 * * *"` (alle 3 h) ändern.
