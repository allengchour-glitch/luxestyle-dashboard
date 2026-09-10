# 🔌 Revid v3 — Render-Payloads nutzen

Fertige Payloads: `content/revid-render-payloads.json` (16 Produkte, je `payload` für `POST /api/public/v3/render`).
Settings je Payload: `script-to-video` · 9:16 · 1080p/30fps · Stock-Video (dynamic) · Voice (de/en) · Captions unten · Musik an · ~20 Sek.

## A) Direkt per cURL (REST)
```bash
curl -X POST https://www.revid.ai/api/public/v3/render \
  -H "key: DEIN_REVID_API_KEY" \
  -H "Content-Type: application/json" \
  -d '<payload aus revid-render-payloads.json>'
```
Response liefert eine Job-/Render-ID; mit `webhookUrl` im Payload (optional) wird das fertige Video gemeldet.

## B) Vollautomatisch via Make.com
1. `webhookUrl` im Payload auf einen **Make.com-Webhook** setzen → Revid meldet das fertige MP4 zurück.
2. Make: Webhook → Google Drive „Upload" (Dateiname = `video_file` aus `reels-schedule-90.csv`) → Posting-Szenario (TikTok/IG/YT/Threads).
3. Trigger der Render-Calls: Make „HTTP → POST" mit dem jeweiligen Payload, getaktet nach Plan.

## C) Über Revid-MCP (damit ein KI-Agent es direkt auslöst)
- Endpoint: `https://www.revid.ai/api/mcp` · Auth: `Authorization: Bearer DEIN_KEY` (oder Header `key`).
- In Claude Code verbinden (einmalig):
  ```bash
  claude mcp add revid --transport http https://www.revid.ai/api/mcp --header "Authorization: Bearer DEIN_KEY"
  ```
- Danach kann Claude die Revid-Render-Tools direkt aufrufen (mit den Payloads oben) — echte Ende-zu-Ende-Automatik.

## Credit-Hinweis (Growth-Plan, 2 000 Credits/Mt)
Jeder Render kostet Credits → mit 1–2 Reels/Tag starten, Verbrauch beobachten, dann skalieren. `outputCount` ggf. auf 1 lassen.
