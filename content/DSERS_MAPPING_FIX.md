# 🔧 DSers-Mapping fixen — „Waterproof 18K Gold Jewelry Set"

**Problem:** Das Shopify-Produkt (SKUs `LX-JWL-GOLD` / `LX-JWL-SILVER`) ist in DSers fälschlich
auf „4pcs Magnetic Clothes Clip" gemappt → Kunde bekäme Wäscheklammern statt Schmuck.
**Ziel:** je Variante den **echten 18K-Edelstahl-Schmuck-Set-Lieferanten** zuordnen.

## Schritt für Schritt (DSers-UI)
1. **app.dsers.com** öffnen → einloggen → Store **luxestyle.ch** wählen.
2. Links **„My Products"** (Meine Produkte) öffnen.
3. Produkt suchen: **„Waterproof Stainless Steel Jewelry Set – 18K Gold"** (oder nach SKU `LX-JWL`).
4. Auf das **Mapping-Icon** (zwei Pfeile / „Mapping") des Produkts klicken.
5. Im Mapping-Fenster Methode **„Basic"** wählen. Du siehst die aktuelle (falsche) Supplier-Zeile „…Clothes Clip".
6. **Richtigen Lieferanten holen:**
   - Auf AliExpress den passenden Artikel suchen: *„18K gold plated stainless steel jewelry set waterproof tarnish free"*.
   - Lieferant mit **echten Fotos**, gutem Preis und **AliExpress Standard/Selection-Versand** wählen → **Produkt-URL kopieren**.
7. In DSers die alte Supplier-URL **ersetzen**: AliExpress-URL einfügen (Feld „Supplier"/„Add supplier") → Produkt laden.
8. **Varianten zuordnen:** für `Gold` und `Silver` je die passende AliExpress-Variante (Farbe) + Ship-from wählen.
9. **Speichern** (Save mapping). Status sollte „Mapped/Verified" zeigen.
10. Optional: in DSers **Preis-/Versandregel** prüfen, damit die CHF-Marge stimmt.

## Danach
→ Hier **„publish gold"** schreiben — dann publishe ich das Gold-Set sofort
(Onlineshop + TikTok), wie bei Diffuser & Lampe.

**Hinweis:** Erst nach korrektem Mapping bewerben — sonst Fehllieferung + Reklamationen + Ad-Risiko.

---
## 📸 Supplier-Bilder nach Shopify pushen (für bessere Reels)
Ziel: Die 3 US/Summer-Produkte (Gold-Set, Rain Cloud Diffuser, Sunset Lamp) haben je nur **1 Bild**.
Mehr echte Fotos vom Lieferanten holen:

**In DSers (Browser):**
1. **app.dsers.com** → Store luxestyle.ch → **Meine Produkte**.
2. Produkt öffnen (z.B. 18K Gold-Set / Rain Cloud Diffuser / Sunset Lamp).
3. Tab **„Bilder" / „Images"** (im Produkt-Edit) → die gewünschten **Supplier-Fotos anhaken**.
4. **„Push to Shopify" / „Mit Shopify synchronisieren"** klicken.
5. Pro Produkt wiederholen.

→ Danach hat jedes Produkt mehrere echte Fotos in Shopify. **Dann Claude Code Bescheid geben**
(„US-Reel bauen") → baut das US/Summer-Reel mit echten Multi-Bildern (Tool `build_reel.py`,
`--shopify-query "tag:US AND tag:Summer 2026"`).

Alternativ ohne Warten: Claude kann ein Reel aus dem 1 Hi-Res-Bild je Produkt per Multi-Crop-Ken-Burns bauen.
