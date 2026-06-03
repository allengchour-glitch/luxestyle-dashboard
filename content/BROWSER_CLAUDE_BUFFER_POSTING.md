# 🤝 Auftrag für Browser-Claude — LuxeStyle Reels auf TikTok + Instagram posten (via Buffer)

**Ziel:** Die 6 ad-safe Reels organisch auf **TikTok + Instagram (+ Threads)** veröffentlichen.
Claude Code kann das nicht direkt (TikTok hat keinen offenen Post-Endpoint; IG braucht Graph-API +
Business-Konto + Token). **Buffer** löst das — und ist im Make-Account bereits vorhanden.

## Die 6 Reels (im Repo, Branch `claude/blissful-albattani-wUQZV`, Ordner `content/ads/`)
- `LuxeStyle_Sommer_AdSafe.mp4` (Sommer-Mix)
- `LuxeStyle_Geschenke_Ihn_AdSafe.mp4` (Für Ihn)
- `LuxeStyle_Wellness_AdSafe.mp4` (Diffuser/Lampen/Projektor)
- `LuxeStyle_Tech_AdSafe.mp4` (Smartwatch/Audio/Charger)
- `LuxeStyle_FuerSie_AdSafe.mp4` (Schmuck & Accessoires)
- `LuxeStyle_Reise_AdSafe.mp4` (Sonnenbrille/Strandtuch/Reise)
Alle 9:16, 11,5s, CHF-Preise, **ad-safe** (keine Bewertungs-/Health-Claims), eigener Beat (lizenzfrei).

## Schritt 1 — Buffer-Kanäle verbinden (einmalig)
1. **buffer.com** einloggen (LuxeStyle).
2. Kanäle verbinden: **TikTok**, **Instagram** (⚠️ als **Business/Creator-Konto**, mit Facebook-Seite
   verknüpft — sonst kein Reel-Posting), optional **Threads**.

## Schritt 2 — Reels einplanen
Für jedes Reel: Video hochladen → **Caption** (unten) → Kanäle TikTok+IG wählen → Zeit setzen
→ **1 Reel pro Tag** (nicht alle auf einmal). Gute Zeiten CH: **12:00, 17:30, 20:00**.

## Caption (DE, copy-paste — pro Tag ggf. Produkt anpassen)
```
✨ LuxeStyle – Premium Accessoires & Gadgets aus der Schweiz 🇨🇭
Sommer 2026 ist da. 10% mit Code WELCOME10 🛍️
#luxestyle #swissmade #schweiz #sommer2026 #accessoires
#geschenkidee #shopping #fyp #foryou #tiktokmademebuyit
```
Instagram: „Link in Bio" ergänzen; Hashtags optional in den ersten Kommentar.

## Schritt 3 (optional) — voll automatisieren über Make
Make-Szenario: **Google Sheet/Drive (Reels + Captions) → Buffer-Modul → TikTok/IG/Threads**.
(Org 7603352 · Team 1667409 · Zone eu1 · Buffer-Connection vorhanden.) Siehe
`content/makecom-autopost-blueprint.md`.

## Wichtig
- **Erst 1 Reel organisch testen** (Engagement ansehen), dann Takt hochfahren — passt zur Strategie
  „zuerst 1 Kunde".
- Captions ad-/policy-safe halten (keine unbelegten Claims). Code `WELCOME10` muss aktiv sein (ist es).
- Performance später mit `content/tools/tiktok_analyze.py` auswerten (Top-Hooks/Hashtags lernen).
