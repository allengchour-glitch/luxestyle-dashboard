# 📼 Produzierte Reels — Session 2026-06-02

Alle 9:16, 1080×1920, yuv420p (TikTok/IG/YT-ready). Quellen = echte Shop-Assets, sofern nicht anders vermerkt.
Dateien wurden dem User als Download geliefert (nicht im Repo, da grosse Binaries). Rezepte:
`revid-custom-media-recipe.md` (Revid) · `reel-build-recipe-ffmpeg.md` (ffmpeg).

## Revid (Premium, ruhiger Stil)
- 5 Reels: Sunset-Test, Mix v1 (dynamisch), Mix v2 (ruhig), Mix v3 (Schmuck+Kleid+Tasche+Tech),
  Schmuck, Smart Ring, LED-Uhr, Diffuser. → **Stock-Lookalikes**, nicht produkttreu.
- **Sommerkleid-Reel** aus 5 echten Shopify-Fotos via `media.type:custom` → **produkttreu** ✅.

## ffmpeg-Montagen (echte Produkt-Demovideos)
- **LuxeStyle_Premium_5er** (v1/v2/v3): Herrenuhr · Smart Diffuser XXL · Flame Diffuser · Notebook&Pen ·
  Diver Pro Automatic (ersetzte Pillow Spray) · später + Sommerkleid + 18K-Gold-Schmuck. ~24–30s.
- **LuxeStyle_15s_smooth** (finale, flüssige TikTok-Version, 14,6s):
  1. Sommerkleid «Savanna» (rot, CHF 39.90) — aus Sommer-Mode-Ad
  2. Off-Shoulder «Brise» (grün, CHF 34.90) — aus Sommer-Mode-Ad
  3. 18K Gold Schmuck-Set (Foto 5760×3840, weicher Zoom)
  4. Diver Pro Automatic (Demo-Video)
  5. Flame Diffuser (Demo-Video)
  6. End-Card (WELCOME10)
  - Flüssig-Fix: Kleider als Standbild + linearer Ken-Burns (kein Slow-Mo-Ruckeln), Zoom in 2×-Präzision.

## Finale TikTok-Ad (ad-safe, nur echte Produkte)
- **`content/ads/LuxeStyle_TikTok_AD_Sommer2026.mp4`** (15,7s) + Poster. Handoff: `BROWSER_CLAUDE_TIKTOK_AD.md`.
- Nur echte, aktive Shop-Produkte mit Preis: Sommerkleid Schwarz (kurz) · Mini-Kleid Rot/Türkis/Weiss · 18K Gold Schmuck-Set · Ohrring-Set 925 · Damen-Armband · Crossbody-Bag Vegan · Flame Diffuser → CTA WELCOME10.
- Ad-safe: Text in TikTok-Safe-Zone (oben/Mitte), lizenzfreie Musik, **kein Fremdlogo** (Uhr „SEA-GULL" bewusst weggelassen).

## Offene Punkte / To-do
- ⚠️ **Savanna/Brise** (und weitere Ad-Kleider) als echte, lieferbare Produkte bestätigen, bevor beworben.
- ⚠️ DSers-Mapping prüfen: „Waterproof 18K Gold Jewelry Set" war auf „Magnetic Clothes Clip" gemappt (falsch).
- Ad-Zähler „01/10 / 04/10" bei Kleidern optional wegcroppen.
- Posten läuft über Buffer/Make (Browser) — Dashboard/Claude liefert nur die fertigen MP4s.
- Optional: Uhr/Diffuser (24fps-Quelle) per `minterpolate` auf glatte 30fps.
