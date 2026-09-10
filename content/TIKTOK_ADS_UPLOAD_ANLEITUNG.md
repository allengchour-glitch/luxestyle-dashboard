# 📲 Anleitung: Reel als TikTok-Ad hochladen (LuxeStyle)

Fertiges Video: `content/ads/LuxeStyle_Mix_Reel_Sommer.mp4` (9:16, 1080p, mit Musik).
Pixel: **D8EQE4JC77UAEKHUJCM0** · Code **WELCOME10** · Ziel-URL **luxestyle.ch**

## 0) Voraussetzungen (einmalig)
- TikTok **Business-Konto** + Zugang zu **ads.tiktok.com** (Ads Manager).
- **Pixel D8EQE4JC77UAEKHUJCM0** im luxestyle.ch-Theme installiert (ist aktiv).
- Zahlungsmethode im Ads Manager hinterlegt.
- Tipp **Spark Ad**: Reel zuerst **organisch** auf dem LuxeStyle-TikTok posten → dann diesen Post bewerben (behält Likes/Kommentare, Bio-Link zählt).

## A) Weg 1 – manuell im Ads Manager (empfohlen)
1. **ads.tiktok.com → Kampagne → Erstellen.**
2. **Ziel:** „Website-Conversions" (Produktverkäufe).
3. **Ad Group:**
   - Optimierungsort **Website** → Pixel `D8EQE4JC77UAEKHUJCM0` wählen.
   - **Optimierungsereignis: „Kauf abschließen / Complete Payment".**
   - **Placement:** manuell → nur **TikTok**, Format 9:16.
   - **Zielgruppe:** Standort **Schweiz**, Alter 18–45, Sprache DE; Interessen Mode/Shopping/Schmuck.
   - **Budget:** Tagesbudget **CHF 15–20**, 3–5 Tage testen.
   - Gebotsstrategie: „Niedrigste Kosten".
4. **Ad (Anzeige):**
   - **Identität:** LuxeStyle-TikTok-Konto auswählen (für Spark Ad „TikTok-Post nutzen/autorisieren"). Sonst Custom Identity mit Logo + Name.
   - **Video hochladen:** `LuxeStyle_Mix_Reel_Sommer.mp4` (oder „aus TikTok-Posts" für Spark).
   - **Text/Caption** (siehe unten) + **CTA-Button „Jetzt einkaufen"** + URL `https://luxestyle.ch`.
   - **Musik:** ist bereits drin (lizenzfrei). Falls Ads Manager nachfragt → Commercial Music Library. **Keine Trending-Pop-Songs in bezahlten Ads.**
5. **Senden** → TikTok-Review (wenige Stunden). Bei Ablehnung meist: Produkt/Preis/Verfügbarkeit prüfen.

**Caption:**
> Sommer 2026 bei LuxeStyle ☀️ Looks für sie & ihn – schon ab CHF 16.90. 10% mit Code WELCOME10. Versand aus der Schweiz 🇨🇭 → luxestyle.ch

**Hashtags:** `#LuxeStyle #SommerMode2026 #SchweizShopping #OOTD #SwissStyle #TikTokMadeMeBuyIt #HerrenMode #Modeschmuck #Sommeroutfit`

## B) Weg 2 – per Tool (API, für Automatisierung)
ENV setzen, dann:
```bash
export TIKTOK_ACCESS_TOKEN=...   # genehmigte TikTok-for-Business-App
export TIKTOK_ADVERTISER_ID=...  # Werbekonto-ID
python content/tools/tiktok_upload.py content/ads/LuxeStyle_Mix_Reel_Sommer.mp4 --name "LuxeStyle Mix Sommer"
```
→ gibt **video_id** zurück → im Ads Manager als Creative auswählen (Schritt A4) oder via Campaign-Endpoints schalten.
Token/Advertiser-ID einmalig im TikTok-Developer-/Business-Portal holen.

## ⚠️ Vor dem Schalten prüfen
- Beworbene Produkte **active + published** mit **korrektem Preis** (per Shopify-API verifizierbar).
- **Keine Fremdmarken-Logos** im Creative (ist hier sauber).
- Reviews-/Claim-Angaben müssen stimmen.
