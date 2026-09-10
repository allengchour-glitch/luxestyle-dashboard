# 🤝 Auftrag für Browser-Claude — TikTok-Anzeige per API schalten

**Ziel:** Die Anzeige **automatisch** anlegen (Kampagne→AdGroup→Ad) mit `content/tools/tiktok_campaign.py`,
statt im Ads Manager zu klicken. Claude Code kann das Tool nicht selbst ausführen (kein Portal-Zugang +
der vorhandene Token ist scope-los → `40001` auf allen Endpoints). Du hast den Browser-/Portal-Zugang.

## Warum nötig
Verifiziert am 2026-06-04: Token `0780fa34…` gibt **`40001` (Permission/scope fehlt)** auf
`/advertiser/info/`, `/identity/get/` und `/file/video/ad/upload/`. Er kann **nichts** im Werbekonto.
→ Ein **neuer Token mit den richtigen Scopes** muss her.

## Schritt 1 — App-Scopes freischalten + autorisieren (Portal)
1. **business-api.tiktok.com/portal** → deine App öffnen.
2. Scopes aktivieren: **Ad Account Management** + **Creative Management** (beide!).
3. Authorization-URL der App im Browser öffnen → Werbekonto **LuxeStyle** zustimmen.
4. In der Redirect-URL steht `?auth_code=XXXX` (nur ~10 Min gültig → zügig).

## Schritt 2 — neuen Access-Token holen
```bash
cd content/tools
python get_token.py            # fragt App ID, Secret, auth_code ab
# Ausgabe: ACCESS_TOKEN + ADVERTISER_IDS + SCOPES (müssen Ads + Creative enthalten)
```

## Schritt 3 — Anzeige anlegen (pausiert) — EIN Befehl
```bash
export TIKTOK_ACCESS_TOKEN="<neuer Token>"
export TIKTOK_ADVERTISER_ID="7646349875793182738"   # LuxeStyle CH
python tiktok_campaign.py --video ../ads/LuxeStyle_Sommer_AdSafe.mp4 --dry-run   # Vorschau
python tiktok_campaign.py --video ../ads/LuxeStyle_Sommer_AdSafe.mp4             # pausiert anlegen
```
Das Tool macht automatisch: Video-Upload → Kampagne **WEB_CONVERSIONS** (kein Katalog/DPA) →
Ad Group (Pixel `D8EQE4JC77UAEKHUJCM0`, **Lowest Cost / kein Target-CPA**, Schweiz, DE+FR, alle Alter,
CHF 20/Tag, nur TikTok) → Ad (Single Video, CTA „Shop Now", Landing `luxestyle.ch`). **Status = PAUSIERT.**

Optionen: `--event COMPLETE_PAYMENT` · `--budget 30` · `--text "..."` · `--live` (sofort aktiv).

## Schritt 4 — prüfen & scharf schalten
Im **Ads Manager** Kampagne „LuxeStyle CH – Sommer" prüfen (Creative ad-safe? Targeting? Budget?) →
auf **AKTIV** schalten. Oder gleich mit `--live` erstellen.

## ⚠️ Sicherheit
- Der **alte Token `0780fa34…` ist im Chat exponiert → revoken/rotieren.** Nur den neuen verwenden.
- Token **nie committen**, nur als ENV/Secret.

## Fallback (ganz ohne API)
Geht der API-Weg nicht: Reel `content/ads/LuxeStyle_Sommer_AdSafe.mp4` **manuell** hochladen,
Kampagnenziel **Website-Conversions** (NICHT Katalog), Bid **Lowest Cost** (kein Target-CPA),
Pixel `D8EQE4JC77UAEKHUJCM0`, Event Add-to-Cart, Schweiz/DE+FR, CHF 20/Tag. (Schritt-für-Schritt
siehe Chat-Verlauf / `content/TIKTOK_ADS_UPLOAD_ANLEITUNG.md`.)
