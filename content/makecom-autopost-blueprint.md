# 🤖 Make.com Auto-Post Blueprint — Reels (TikTok · Instagram · YouTube Shorts · Threads)

Ziel: vollautomatisches Posten der Reels nach Plan. **Einmal einrichten → läuft täglich allein.**
Quelle: `content/reels-schedule-90.csv` (3 Reels/Tag, 30 Tage) bzw. `reels-schedule.csv`/`-30d.csv`.

## Architektur
```
[AI-Video-Tool] --MP4(9:16)--> [Google Drive Ordner]
                                       │
[Google Sheet: reels-schedule] --------┤
                                       ▼
                              [Make.com Szenario (alle 20 Min)]
                                       │ Filter: date=heute & time<=jetzt & status<>posted
                                       ▼
        ┌──────────────┬───────────────┬───────────────┬─────────────┐
     TikTok        Instagram        YouTube           Threads
   Upload Video    Publish Reel    Shorts Upload    Publish Video
```

## Schritt für Schritt
1. **Sheet anlegen:** `reels-schedule-90.csv` in Google Drive → als Google Sheet importieren. Spalte `status` ergänzen (leer).
2. **Drive-Ordner** „reels/" — dort liegen die MP4s; Dateiname **exakt** = Spalte `video_file`.
3. **Make.com Szenario:**
   - **Trigger:** Schedule, alle 15–20 Min.
   - **Google Sheets → Search Rows:** Filter `date` = `{{formatDate(now;YYYY-MM-DD)}}` UND `status` ist leer UND `time_cet` ≤ jetzt.
   - **Google Drive → Get a File:** by name = `{{video_file}}`.
   - **Router** → 4 Branches:
     - **TikTok** (Module „Upload a Video"): Video = Drive-Datei, Caption = `{{caption}} {{hashtags}}`.
     - **Instagram for Business** („Create a Reel"): Video-URL, Caption = `{{caption}} {{hashtags}}`.
     - **YouTube** („Upload a Video", #Shorts): Title = `{{hook}}`, Description = `{{caption}} {{hashtags}}`, 9:16 + „#Shorts".
     - **Threads** (Meta Threads „Publish a Post" / via Buffer): Text = `{{caption}}`, Media = Video.
   - **Google Sheets → Update Row:** `status` = `posted`.
4. **Accounts verbinden:** TikTok (Business), Instagram (Business via Facebook Page), YouTube (Google), Threads (via Meta/Buffer-Connector).

## Plattform-Hinweise
- **Ein 9:16-Video** funktioniert für alle 4 (TikTok / IG Reels / YT Shorts / Threads).
- **TikTok/IG**: direkte Make.com-Module vorhanden.
- **YouTube Shorts**: normales Upload-Modul, vertikal + „#Shorts" im Titel/Desc.
- **Threads**: noch kein natives Make-Modul überall → über **Buffer/Publer**-Connector oder Meta Graph posten.

## Video-Engine (eine wählen, mit Make.com koppelbar)
- **Revid.ai / Predis.ai / InVideo AI** → erzeugen Reels aus Produktbild+Caption automatisch (API/Zapier/Make).
- Oder eigene Clips → Adobe `video_resize` auf 9:16.
- Dateien landen im Drive-Ordner → Schritt 2.

> Sobald Video-Engine + Make-Szenario stehen, postet das System die 90 Reels vollautomatisch nach Zeitplan. Claude Code liefert Plan/Captions/CSV; Aufbau der Maschine erfolgt in Make.com (Browser).
