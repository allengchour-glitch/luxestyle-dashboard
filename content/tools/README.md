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
