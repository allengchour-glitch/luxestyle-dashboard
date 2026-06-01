# LuxeStyle Dashboard

Internes Single-Page-Dashboard für den Dropshipping-/Mode-Shop **LuxeStyle**.
Statisches HTML/CSS/JS ohne Build-Step, Deploy über Netlify.

## Überblick

Das gesamte Dashboard steckt in **einer Datei**: `index.html` (HTML, CSS und JS inline).
Alle benutzerpflegbaren Daten liegen im **`localStorage`** des Browsers – es gibt kein
eigenes Backend für diese Daten.

Zwei separate Shops werden geführt:

- **luxestyle.com.co** – Haupt-Shopify-Shop
- **luxestyle.ch** – separater Shop für die TikTok-Sommer-Kampagne

## Lokal öffnen

Kein Server nötig – einfach `index.html` im Browser öffnen:

```bash
open index.html        # macOS
xdg-open index.html    # Linux
```

Alles läuft client-seitig; Netlify wird nur für den Live-Betrieb und die
Shopify-Functions gebraucht.

## Tabs

`overview` (Cockpit) · `products` · `marketing` · `affiliate` · `pipeline` ·
`launchpad` · `stats` · `content` · `settings`

## Projektstruktur

| Pfad | Zweck |
|---|---|
| `index.html` | Das Dashboard – hier passiert praktisch alles |
| `netlify/functions/` | Shopify-Anbindung (OAuth-Callback, Proxy) |
| `netlify.toml` | Netlify Build & Headers |
| `tiktok_videos.json` | Quelle für den Content-Tab (Video-Pipeline) |
| `snippets/tiktok-pixel-luxestyle-ch.html` | TikTok-Pixel für den luxestyle.ch-Storefront (nicht ins Dashboard einbauen) |
| `CLAUDE.md` | Projekt-Memory / Entwickler-Notizen |

## Deploy

Push auf den Entwicklungs-Branch, anschließend Deploy über Netlify.
Details und Konventionen siehe [`CLAUDE.md`](./CLAUDE.md).
