# 🚫 Shop-Compliance — Produkte offline nehmen (IP-/Markenrecht)

Beim Erstellen der Herren-Ads gefunden: mehrere CJ-Herren-Apparel-Produkte mit **Fremdmarken-Logos
(Counterfeit)** bzw. **Lieferanten-Wasserzeichen**. Diese **nicht bewerben/verkaufen** → in Shopify
**Status = Entwurf** (oder Archiviert) setzen. (Entwurf ist reversibel.)

| Produkt (Titel) | Handle | Problem | Aktion |
|---|---|---|---|
| Herren Sommer-Set · Shorts + Rundhals-T-Shirt | `herren-sommer-mode-markenkleidung-lassige-business-shorts-locker-geschnittenes-vielseitiges-rundhals-t-shirt-atmungsaktives-t-shirt` | **„POLO" + Ralph-Lauren-Reiter** (Fälschung) | auf Entwurf |
| Herren Gym-Shirt · Muscle-Fit | `herren-workout-muskel-kleidung-gym-bodybuilding-t-shirt-sommer-baumwolle-kurzarm-casual-sportbekleidung-fitness-atmungsaktive-shirts` | **Superman-Logo** (DC, Fälschung) | auf Entwurf |
| Herren Tracksuit-Set 2-tlg | `mode-kleidung-set-fur-manner-tracskuit-set-casual-walking-anzug-ovrersize-streetwear-langarm-t-shirt-hosen-outfit-2-stuck` | eingebranntes Lieferanten-Wasserzeichen „Forest Store" | Bild ersetzen ODER Entwurf |

## Manuell in Shopify (1 Min)
Admin → **Produkte** → Produkt öffnen → **Status: Entwurf** → Speichern. (Oder Mehrfachauswahl → Aktion „Als Entwurf festlegen".)

## Automatisch (sobald Shopify-API wieder erreichbar)
Claude/Tool kann `bulk-update-product-status` → DRAFT für die obigen Handles ausführen.
Hinweis: weitere CJ-Apparel-Bilder mit Fremdmarken können existieren → ganzes Herren-Apparel-Sortiment sichten.

---
## ✅ ERLEDIGT 2026-06-02 (von Claude via Shopify-API)
Alle 3 auf **ARCHIVED** gesetzt (offline, reversibel):
- `gid://shopify/Product/15413245772161` — Herren Sommer-Set (POLO) ✅
- `gid://shopify/Product/15413245837697` — Herren Gym-Shirt (Superman) ✅
- `gid://shopify/Product/15413245739393` — Herren Tracksuit-Set (Wasserzeichen) ✅
Endgültiges Löschen optional im Admin. Restliches Herren-Apparel-Sortiment noch auf weitere Fremdmarken sichten.
