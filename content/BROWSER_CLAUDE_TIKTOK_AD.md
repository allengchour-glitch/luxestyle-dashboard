# 📲 Browser-Claude-Auftrag — TikTok-Ad „LuxeStyle Sommer 2026"

**Ziel:** Die fertige Ad organisch posten **und** als TikTok-Ad (Spark Ad) schalten. Claude Code hat die Ad
produziert; das Klicken in TikTok Ads Manager / Buffer / DSers passiert hier (Browser).

## 1) Asset
- **Video:** `content/ads/LuxeStyle_TikTok_AD_Sommer2026.mp4` (PRO-Version, 9:16, 1080×1920, 15,9s, yuv420p, lizenzfreie Musik)
- **Poster:** `content/ads/LuxeStyle_TikTok_AD_Sommer2026_poster.jpg`
- **Aufbau (PRO):** Hook „SOMMER-SALE −10% WELCOME10" (Sek.1) → Kleider/Schmuck/Tasche/Diffuser (abwechselnde slide/fade-Transitions) → Social-Proof ★★★★★ „Über 50 Bewertungen" → CTA-Endcard. Hellere/pulsierende Musik.
- Inhalt (alle **per Shopify-API verifiziert**: active, published, Preis stimmt): Sommerkleid Schwarz (kurz, 32.90) · Mini-Kleid Rüschen Rot/Türkis/Weiss (29.90) · Ohrring-Set 925 (**22.90**) · Damen-Armband Edelstahl (24.90) · Crossbody-Bag Vegan (34.90) · Flame Diffuser (49.90) → CTA WELCOME10.
- **18K Gold-Schmuck-Set wurde bewusst ENTFERNT** (siehe unten) — kann später wieder rein, sobald published + Mapping gefixt.

## 2) Status der Pre-Launch-Checks (Shopify-API geprüft, Stand 2026-06-02)
- ✅ **Inventar: KEIN Blocker.** Alle Produkte haben `inventory tracking = aus` → in Shopify **immer verkaufbar**, auch bei Anzeige „0".
- ✅ **Preise im Video stimmen** mit dem Shop überein (Ohrring-Set wurde von 29.90 auf korrekte **22.90** gefixt).
- ✅ **Beworbene Produkte sind active + published** (CH).
- ⏳ **Nur falls 18K Gold-Set später beworben werden soll:** (a) Produkt **publishen** (`publishedAt` war `null`), (b) **DSers-Mapping fixen** (war fälschlich „4pcs Magnetic Clothes Clip" → echter 18K-Edelstahl-Lieferant). Dann sagt Claude Code Bescheid und baut es wieder ein.

## 3) Organisch posten (Buffer)
- Kanäle: TikTok (+ optional IG Reels / Threads).
- **Caption (DE):**
  > Sommer-Favoriten von LuxeStyle ☀️ Kleider, Schmuck & Accessoires – jetzt 10% mit Code **WELCOME10**. Versand aus der Schweiz 🇨🇭 → luxestyle.ch
- **Hashtags:**
  `#LuxeStyle #SommerMode2026 #SchweizShopping #Sommerkleid #Modeschmuck #CrossbodyBag #OOTD #SwissStyle #TikTokMadeMeBuyIt #Sommeroutfit #onlineshopping #fashionfinds`
- Tipp: In TikTok einen **Trending-Sound** drüberlegen (nur für *organische* Posts erlaubt).

## 4) Als Ad schalten (TikTok Ads Manager — Spark Ad)
1. **Spark Ad** verwenden → den geposteten organischen TikTok-Post boosten (behält Likes/Kommentare, Bio-Link zählt).
2. **Ziel:** Website-Conversions / Produktverkäufe. **Pixel `D8EQE4JC77UAEKHUJCM0`** (luxestyle.ch).
3. **Optimierungsereignis: Complete Payment** (offener Punkt aus CLAUDE.md — Event muss feuern).
4. **Placement:** nur TikTok, 9:16.
5. **Zielgruppe:** CH, 18–45, Interessen Mode/Schmuck/Shopping. (Für US/Markets EN-Version anfragen.)
6. **Budget:** klein starten (CHF 15–20/Tag), 3–5 Tage testen, dann skalieren.
7. **CTA-Button:** „Jetzt shoppen" → luxestyle.ch.
8. **Musik:** Bed ist lizenzfrei (ad-safe). Falls gewünscht, in Ads Manager auf **Commercial Music Library** wechseln. **Keine** Trending-Pop-Songs in bezahlten Ads.

## 5) Nach dem Launch
- CAPI/Pixel-Events prüfen (View → AddToCart → Complete Payment).
- Bei Ablehnung: meist „Produkt nicht verfügbar/Preis" → Inventar/Mapping (Punkt 2) prüfen.

## Hinweis zu Foto-/Markenrechten
- Uhr-Demo („SEA-GULL"-Logo) wurde **bewusst weggelassen** (Fremdmarke). Keine Fremdlogos in der Ad.
- Englische Version (für US-Market, USD-Preise) kann Claude Code auf Wunsch erstellen.

## 6) Performance-Feedback & Empfehlungen (für bessere Resultate)
- **Wahrheits-Check:** „Über 50 Bewertungen" nur lassen, wenn auf `luxestyle.ch` wirklich vorhanden (Loox). Sonst Zahl anpassen/entfernen.
- **Grösster Hebel = echtes UGC:** 10-Sek-Handyvideo mit echter Person (Try-on/Unboxing, gesprochen) performt auf TikTok deutlich besser als die Slideshow. Idealerweise über Creator/Affiliate-Programm.
- **Skalierung:** zusätzlich kategorie-spezifische Ads (nur Kleider / nur Schmuck) → schärfere Zielgruppe, tieferer CPM.
- **Echte Kundenfotos** (Loox-UGC) statt Stock-Model-Bilder erhöhen Trust.
- **Musik:** Bed ist lizenzfrei. Für organische Posts zusätzlich Trending-Sound; in bezahlten Ads nur Commercial Music Library.
