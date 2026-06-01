# 🎬 14-Tage Reel-Posting-Plan — LuxeStyle (US/Summer 2026)

**Ziel:** 1 Reel/Tag, parallel auf **TikTok + Instagram Reels**. Captions EN (US/Global-Fokus) — DE-Varianten sind im Dashboard (Content-Tab → 🎬 Mode-Creatives + 💬 Antworten).
**Automatisierung:** `content/reels-schedule.csv` in Make.com einlesen (Google Sheets / CSV-Modul) → Posting-Modul TikTok + Instagram. Zeiten in **CET**.
**Code:** WELCOME10 (-10 %) durchgehend, am Schluss USA15 (-15 %) als Sale-Push.

## Posting-Kalender
| Tag | Datum | Zeit | Produkt | Format | Hook |
|---|---|---|---|---|---|
| 1 | 02.06 | 19:00 | 🌅 Sunset Lamp | POV | „POV: your room just became the comfiest spot" |
| 2 | 03.06 | 18:00 | ☁️ Rain Cloud Diffuser | ASMR/aesthetic | „This cloud actually rains" |
| 3 | 04.06 | 20:00 | 💍 Jewelry Set | Try-on | „Jewelry that survives the pool" |
| 4 | 05.06 | 19:30 | 📱 Phone Set | Makeover | „Phone glow-up in 10 seconds" |
| 5 | 06.06 | 12:00 | ⏰ LED Clock | Desk-Setup | „The desk detail everyone asks about" |
| 6 | 07.06 | 17:00 | 👜 Straw Bag | Summer-Outfit | „The only bag I'm bringing this summer" |
| 7 | 08.06 | 19:00 | 🌅 Sunset Lamp | GRWM | „GRWM with golden-hour lighting" |
| 8 | 09.06 | 20:00 | 💍 Jewelry Set | Unboxing | „Unboxing my waterproof gold set" |
| 9 | 10.06 | 18:30 | ☁️ Diffuser | Before/After | „Turn your room into a spa" |
| 10 | 11.06 | 19:00 | 📱 Phone Set | Charms-Haul | „Which charm is your fave?" |
| 11 | 12.06 | 12:30 | 👜 Straw Bag | Beach-Day | „Beach day essentials" |
| 12 | 13.06 | 20:00 | ⏰ LED Clock | Aesthetic Night | „Minimal desk, maximum vibe" |
| 13 | 14.06 | 17:30 | 💍 Jewelry Set | Layering | „Summer layering that lasts" |
| 14 | 15.06 | 19:00 | 🌅 Sunset Lamp | Sale-Push | „Last days: −15 % mit USA15" |

## Rhythmus-Logik
- **Produkt-Rotation:** jedes der 6 Produkte 2–3×, mit wechselndem Format (POV · GRWM · Unboxing · Try-on · Before/After · Sale) → kein Wiederholungs-Gefühl.
- **Beste Zeiten (CET):** Abends 17–20 Uhr (Feierabend-Scroll) + 1–2 Mittags-Slots (12:00/12:30) für Reichweiten-Tests.
- **Hooks** in den ersten 2 Sek. — entscheidend für Watch-Time.
- **CTA** immer: „link in bio" + Code.

## So in Make.com einrichten
1. **Trigger:** Schedule (täglich) **oder** Google Sheets „Watch Rows".
2. **Quelle:** `reels-schedule.csv` (in Google Drive ablegen / als Sheet importieren).
3. **Filter:** Zeile, deren `date` = heute.
4. **Module:** TikTok (Upload Video) + Instagram (Publish Reel) → Felder `caption` + `hashtags`, Video aus `video_file`.
5. **Video-Quelle:** Drive-Ordner mit den `*.mp4`-Dateien (Dateinamen = Spalte `video_file`).

## Spalten der CSV
`date · time_cet · platform · product · sku · format · hook · caption · hashtags · code · lang · video_file · link`

> Hinweis: Die Videodateien (`*.mp4`) müssen noch produziert/hochgeladen werden (z. B. via CapCut/VEO; Adobe `video_resize` bringt sie auf 9:16). Dateinamen exakt wie in `video_file`.
