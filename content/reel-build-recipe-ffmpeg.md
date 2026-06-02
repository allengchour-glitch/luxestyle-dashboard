# 🛠️ Reel-Bau ohne Revid — ffmpeg-Montage aus echten Shop-Videos/-Fotos

Premium-9:16-Reel lokal aus echten Shopify-Produkt-Videos (`content/shopify-product-videos.json`)
und/oder Produktfotos bauen. Voll kontrolliert: Crop, Branding, Captions, Transitions, Musik.

## Umgebung
- ffmpeg via `python3 -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"`.
  **Achtung:** dieser Static-Build hat **kein `drawtext`** (kein libfreetype) → Texte als **PNG-Overlay**
  mit Pillow erzeugen und per `overlay` einblenden.
- Fonts: `/mnt/skills/examples/canvas-design/canvas-fonts/BigShoulders-Bold.ttf` (Wordmark, Fashion-Look),
  `/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf` (Captions, hat Umlaute & ·).
- Ausgabe immer **`-pix_fmt yuv420p`** + `+faststart` (sonst TikTok/IG/YT-Inkompatibilität; xfade
  liefert sonst yuv444p).

## Bausteine
1. **Normalisieren auf 9:16 (Blur-Fill):** Hintergrund = Clip `scale=increase,crop=1080:1920,gblur`,
   Vordergrund = scharfes Produkt `scale=1040:-2` mittig drüber. Funktioniert für quer/quadrat/hoch.
2. **Lieferanten-Texte wegcroppen** (z. B. Notebook „100 SHEETS/DISPLAY"): `crop=B:H:X:Y` vor dem Fill.
3. **Branding/Captions:** PNG-Overlay (1080×1920, transparent) mit „LUXESTYLE"-Wordmark oben,
   Gold-Linie (`#C9A24B`) + 2-zeiliger Caption unten; per `overlay=0:0` drauf.
4. **Flüssiger Ken-Burns aus Standbild (kein Ruckeln!):**
   - Standbild in **2× Zielauflösung** (2160×3840) vorrendern (lanczos + unsharp).
   - `-framerate 30 -loop 1 -t DUR` + `zoompan=z='1+0.07*on/N':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30`.
   - **Linearer** Zoom über `on/N` (nicht `zoom+0.0009` — das kompoundiert/ruckelt). 2×-Quelle = subpixel = jitterfrei.
   - **Slow-Mo von echtem Video vermeiden** (`setpts=2.0*PTS` dupliziert Frames → Ruckeln). Lieber Standbild + Zoom,
     oder `minterpolate=fps=30` für echtes Video mit 24fps-Quelle.
5. **Transitions:** `xfade=transition=fade:duration=0.4:offset=<kumuliert-0.4>` zwischen Segmenten.
6. **Musik-Bed (lizenzfrei, selbst erzeugt):** 4 `sine`-Töne (A-Moll-Pad) → `amix,tremolo,lowpass,aecho,volume=0.16,afade`.
   Für TikTok besser In-App-Trending-Sound drüberlegen.

## Bewährte Reihenfolge & Pacing
- Premium-Mix ~24–30s: je Produkt ~4–5s. Straffe TikTok-Version 15s: je Beat ~2,5–3s, `xfade` 0.4.
- End-Card (statisch, ~2,5s): „LUXESTYLE · WELCOME10 = 10% · luxestyle.ch".

## Qualitäts-Caveats (ehrlich)
- Manche Demo-Clips zeigen **Fremdmarken** (Uhr „SEA-GULL", Pillow Spray „South Moon") → ggf. Segment ohne Logo wählen.
- Notebook-Clip hat eingebrannte Lieferantentexte → wegcroppen.
- Die Ad-Kleider («Savanna» rot, «Brise» grün, …) sind **KI-Ad-Konzepte mit Preis-Overlay** —
  vor Bewerbung prüfen, ob als echtes Produkt lieferbar.
