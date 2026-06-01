# 🎬 30-Tage Reel-Plan — LuxeStyle (Mix: Herren · Schmuck · US/Summer · Tech · Wellness)

**1 Reel/Tag · TikTok + Instagram · bilingual** (DE für DACH-Herren-/Lifestyle-Produkte, EN für US/Summer & Schmuck).
Daten/Quelle: `content/reels-schedule-30d.csv` → in Make.com einlesen.
Zeitraum: 16.06.–15.07.2026. Code: WELCOME10 durchgehend, USA15 Sale-Push am Schluss.

## Produkt-Mix (15 Produkte rotiert)
- **Herren:** Signet-Ring matt · Herren-Siegelring schwarz/silber · Plain Band Ring · Leder-Schlüsselanhänger (Gravur) · Smart Ring Titan
- **Schmuck:** Waterproof Gold Set · Stacking-Ring Mix-Metall · Initialen-Ring A–Z · Schmuckbox · Reise-Schmuckbinder
- **US/Summer:** Rain Cloud Diffuser · Sunset Lamp · LED Mirror Clock · Phone Makeover Set · Straw Beach Tote
- **Tech/Wellness:** Ultraschall-Reiniger · Ringlicht 26cm · Akupressur-Ringe · Yoga-Strap

## Format-Rotation (Abwechslung = mehr Watch-Time)
POV · GRWM · Unboxing · Try-on · Before/After · How-to-wear · Demo · Satisfying/CleanTok · Gift · Sale-Push.

## Spalten der CSV
`day · date · time_cet · platform · product · niche · format · hook · caption · hashtags · code · lang · video_file · link`

## Make.com-Setup (Kurz)
1. CSV in Google Drive → als Sheet importieren.
2. Make.com: Schedule (täglich) → Google Sheets „Search Rows" (Filter `date` = heute).
3. Module: TikTok „Upload Video" + Instagram „Publish Reel" → `caption` + `hashtags`, Video = `video_file` aus Drive-Ordner.
4. Videodateien (`*.mp4`, 9:16) im Drive-Ordner mit exakt diesen Dateinamen ablegen.

## ⚠️ Video-Quelle nötig
Die `*.mp4`-Dateien müssen existieren. Optionen: eigene Clips (→ Adobe `video_resize` auf 9:16), CapCut/Canva, oder ein Faceless-/AI-Reel-Tool (Revid, Predis.ai, InVideo), das Make.com ebenfalls anbinden kann.
