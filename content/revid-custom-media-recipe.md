# 🎬 Revid — eigene Produktfotos/-videos statt Stock (Custom Media)

Damit Reels **echte Shop-Produkte** zeigen (nicht ähnliches Stock-Material), unterstützt die
Revid-`/api/public/v3/render`-API eigene Medien über `media.provided`.

## Wichtige Felder (aus der OpenAPI-Spec)
- `media.type: "custom"` — **Pflicht**, sobald `useProvidedInOrder` genutzt wird
  (Fehler sonst: *„media.useProvidedInOrder is only supported when media.type is custom."*).
- `media.provided: [{ "type":"image"|"video", "url": "..." }]` — eigene Medien (z. B. Shopify-CDN-URLs).
- `media.useOnlyProvided: true` — **nur** die eigenen Medien verwenden (kein Stock dazumischen).
- `media.useProvidedInOrder: true` — Medien in Reihenfolge auf die Skript-Abschnitte mappen.
- `media.turnImagesIntoVideos: true` — Standbilder werden animiert (Ken-Burns-artig).

## Funktionierendes Beispiel (Sommerkleid aus 5 echten Shopify-Fotos)
```json
{
  "workflow": "script-to-video",
  "aspectRatio": "9:16",
  "source": { "text": "Ein Kleid, drei Anlaesse. ... Code WELCOME10. Link in Bio." },
  "media": {
    "type": "custom",
    "animation": "soft",
    "quality": "ultra",
    "useOnlyProvided": true,
    "useProvidedInOrder": true,
    "turnImagesIntoVideos": true,
    "provided": [
      { "type": "image", "url": "https://cdn.shopify.com/s/files/.../bild1.jpg" },
      { "type": "image", "url": "https://cdn.shopify.com/s/files/.../bild2.jpg" }
    ]
  },
  "voice": { "enabled": true, "language": "de" },
  "captions": { "enabled": true, "position": "bottom" },
  "music": { "enabled": true },
  "render": { "resolution": "1080p", "frameRate": 30 },
  "options": { "language": "de", "outputCount": 1 }
}
```

## Bild-URLs aus Shopify holen (Admin-API)
GraphQL `nodes(ids:[...]) { ... on Product { media(first:10){ edges{ node{ ... on MediaImage { image{ url width height } } } } } } }`
→ Original-CDN-URLs (teils sehr hochauflösend, z. B. Gold-Schmuck-Set 5760×3840 — ideal für Zoom).

## Caveats / Lessons learned
- **Umlaute in Captions:** im `source.text` echte Umlaute nutzen (Revid-Voice/Caption kann ä/ö/ü).
  Bei eigenem ffmpeg-Overlay (s. `reel-build-recipe-ffmpeg.md`) ebenfalls echte Umlaute via PNG.
- **Produkttreue:** Stock-Workflow (`type:stock-video`) liefert nur *ähnliche* Optik — für echte
  Produkttreue immer `custom` + `provided` nutzen, sonst Reklamationsgefahr („sieht anders aus").
- **Credits:** jeder Render kostet Credits (Growth-Plan 2 000). Klein testen.
- **Render-Key:** im Header `key: <REVID_KEY>` (oder `Authorization: Bearer`). Key nicht committen.
