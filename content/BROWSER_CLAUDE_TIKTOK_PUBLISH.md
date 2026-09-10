# 🤝 Browser-Claude — TikTok-Anzeige fertig veröffentlichen

Copy-paste-Befehl für Browser-Claude, um die Kampagne **„LuxeStyle CH – Sommer Test"** im
TikTok Ads Manager bis **Publish** durchzuklicken. Behebt: leere Ad Group, Katalog/DPA,
Target-CPA, Targeting, Text, Compliance.

```
Aufgabe: Veröffentliche meine TikTok-Anzeige im TikTok Ads Manager (Konto „LuxeStyle CH Ads").
Kampagne: „LuxeStyle CH – Sommer Test". Mach das Schritt für Schritt bis die Ad live ist.

1) FEHLER „All ad groups must contain at least 1 ad":
   - „View ad group without ads" klicken. Es gibt eine LEERE Anzeigengruppe.
   - Duplikat? -> leere Ad Group LÖSCHEN (⋯ → Delete). Sonst: eine Ad anlegen (Single Video, s. u.).

2) KAMPAGNENTYP = „Website Conversions", NICHT Katalog/DPA.
   - Falls Creatives einen Katalog nutzen (z. B. Trinkflasche statt meiner Reels):
     „Creative assets" → „Edit selections" → Katalog-Creatives ABWÄHLEN, nur meine Reels behalten.

3) CREATIVE: Single Video, meine ad-safe Reels (Repo content/ads/):
   LuxeStyle_Sommer_AdSafe.mp4, LuxeStyle_FuerSie_AdSafe.mp4, LuxeStyle_Tech_AdSafe.mp4,
   LuxeStyle_Wellness_AdSafe.mp4, LuxeStyle_Reise_AdSafe.mp4, LuxeStyle_Geschenke_Ihn_AdSafe.mp4.
   Min. 1, gern mehrere. KEINE Fremd-/Katalogprodukte.
   - Ad-Text: „Entdecke LuxeStyle – Premium aus der Schweiz. 10% mit Code WELCOME10."
   - CTA: „Shop Now". Landing: https://luxestyle.ch
   - Promo-Code: nur „WELCOME10". Anderen „Extra 10% off" entfernen.

4) AD GROUP:
   - Optimization location: Website. Pixel: D8EQE4JC77UAEKHUJCM0. Event: „Add to cart".
   - „Set target CPA" AUS → Bid = Lowest Cost / Maximum Delivery (KEIN Bid-Preis).
   - Placement: nur TikTok. „Automatic creative optimization" aus.
   - Targeting: SWITZERLAND, alle Alter, Sprachen DE + FR, Interessen leer.
   - Budget: CHF 20/Tag.

5) COMPLIANCE: keine unbelegten Bewertungs-/Sterne-Claims, keine Health-Claims
   (anlauffrei/hypoallergen/Anti-Aging), keine Fremdmarken-Logos. Reels sind bereits sauber.

6) „Publish all". Bei Ablehnung: Ad-Ebene -> genauen Grund pro Creative lesen, berichten,
   wo möglich „Appeal" klicken.

Status + Screenshot geben, wenn „In review"/live.
```

**Hintergrund (für Browser-Claude):** Pixel `D8EQE4JC77UAEKHUJCM0`, Code `WELCOME10` ist aktiv.
Ad-Compliance-Regeln: `CLAUDE.md` → „⚖️ TikTok-Ad-Compliance". Reels-Quelle: `content/ads/*AdSafe.mp4`.
