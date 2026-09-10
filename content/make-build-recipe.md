# 🛠️ Make.com — Build-Rezept: „LuxeStyle Reels Autopost"

Für **Browser-Claude** (Make-UI). Ziel: aus dem Reel-Plan automatisch Videos generieren (Revid, Premium-Look) und auf **TikTok/Instagram/Threads (via Buffer)** + **YouTube Shorts** posten, mit **Discord-Benachrichtigung**.
Make-Account: Org 7603352 · Team 1667409 · Zone eu1. Vorhandene Connections: Shopify, **YouTube**, Gmail, **Buffer**.

> ⚠️ Den geklonten „ABAN Files"-Flow NICHT verwenden — der ist ein Sci-Fi-Avatar-Pipeline (HeyGen) und off-brand. Neu bauen.

## Voraussetzung
- **Revid-API-Key** (Growth-Plan) — für die Premium-Produkt-Reels. (HeyGen-Avatare sind für Produkte off-brand → nicht nutzen.)
- Schedule als Google Sheet (Quelle: `content/reels-schedule-90.csv`).
- Revid-Payloads: `content/revid-render-payloads.json` (Premium-`stylePrompt` + `quality:ultra`).
- Discord-Webhook-URL (aus eurem Discord-Channel).

## Szenario A — „Reel generieren" (alle 8 Std bzw. 3×/Tag)
1. **Google Sheets → Search Rows**: Filter `date`=heute & `time_cet`≤jetzt & `status` leer.
2. **HTTP → POST** `https://www.revid.ai/api/public/v3/render`
   - Header: `key: REVID_KEY`
   - Body: Payload aus `revid-render-payloads.json` zum `product` der Zeile (script-to-video, 9:16, quality ultra, stylePrompt = Premium/clean, **kein Billig-Stock**).
   - `webhookUrl`: Webhook von Szenario B.
3. **Google Sheets → Update Row**: `status`=`rendering`.

## Szenario B — „Posten" (Webhook von Revid bei Fertigstellung)
1. **Webhook** (empfängt fertige Video-URL von Revid).
2. **HTTP → Download** Video.
3. **Buffer → Create Post**: Channels TikTok+Instagram+Threads · Text = `caption`+`hashtags` · Media = Video.
4. **YouTube → Upload Video** (#Shorts): Title=`hook`, Description=`caption`+`hashtags`, **privacyStatus für Tests = `private`**, später `public`.
5. **Discord** (HTTP POST an Discord-Webhook): „✅ Live: {{product}} auf TikTok/IG/Threads/YouTube — {{date}} {{time}}".
6. **Google Sheets → Update Row**: `status`=`posted`.

## Test-Vorgehen („bis es geht")
1. YouTube privacy auf **private**, Buffer-Post als **Draft/Queue** statt sofort.
2. 1 Zeile manuell durchlaufen lassen → Revid-Render prüfen (Qualität! Premium, kein Billig-Stock).
3. Wenn Video gut → Buffer/YouTube scharf schalten, Discord-Notify testen.
4. Scheduling aktivieren (3×/Tag bzw. nach Plan).

## Credit-Hinweis
Revid Growth = 2 000 Credits. Beim Testen klein halten, dann skalieren.
