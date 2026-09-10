# LuxeStyle Dashboard

Internes Single-Page-Dashboard für den Dropshipping-/Mode-Shop **LuxeStyle**,
plus die Automations-Tools rund um Shop, Reels und Social-Posting.
Statisches HTML/CSS/JS ohne Bundler, Deploy über Netlify.

## Überblick

Das Dashboard selbst steckt in **einer Datei**: `index.html` (HTML, CSS und JS inline).
Alle benutzerpflegbaren Daten liegen im **`localStorage`** des Browsers – es gibt kein
eigenes Backend dafür. Die Netlify-Functions sprechen ausschließlich mit Shopify.

Zwei separate Shops werden geführt:

- **luxestyle.com.co** – Haupt-Shopify-Shop
- **luxestyle.ch** – separater Shop für die TikTok-Kampagne, mit eigenem Pixel

Rund um das Dashboard liegt unter `content/` eine gewachsene Werkzeugkiste:
Reel-Bau, Social-Posting und der Newsletter „aban news Pro". Diese Tools sind
eigenständig (Python, nur stdlib plus optionale Extras) und hängen nicht am Dashboard.

## Lokal öffnen

Kein Server nötig – einfach `index.html` im Browser öffnen:

```bash
open index.html        # macOS
xdg-open index.html    # Linux
start index.html       # Windows
```

Alles läuft client-seitig; Netlify wird nur für den Live-Betrieb und die
Shopify-Functions gebraucht.

## Prüfen vor dem Commit

```bash
npm run build     # bzw. npm run check – dasselbe
```

Es gibt keinen Bundler; der „Build" ist ein Validierungslauf und prüft,
was sonst erst live auffällt:

- `index.html`: genau drei Inline-Script-Blöcke, jeder syntaktisch valide
- `index.html`: `<div>` / `</div>` ausgeglichen
- `netlify/functions/*.js` per `node --check`

Reines Node, keine Abhängigkeiten, läuft auch unter Windows. Exit-Code 1 bei Fehlern.

## Tabs

`overview` (Cockpit) · `products` · `marketing` · `affiliate` · `pipeline` ·
`launchpad` · `stats` · `content` · `settings`

Tab-Wechsel über `showTab(event, 'id')`, aus anderen Tabs heraus `showTab(null, 'id')`.

## Projektstruktur

| Pfad | Zweck |
|---|---|
| `index.html` | Das Dashboard – hier passiert praktisch alles |
| `scripts/build-check.mjs` | Validierungslauf hinter `npm run build` |
| `scripts/install_browser.sh` | Chromium für die Browser-Automation nachinstallieren |
| `netlify/functions/` | Shopify-Anbindung (OAuth-Callback, Proxy) |
| `netlify.toml` | Netlify: publish-Verzeichnis, Functions, Security-Header |
| `package.json` | npm-Skripte und die einzige Laufzeit-Abhängigkeit (`@netlify/blobs`) |
| `tiktok_videos.json` | Quelle für den Content-Tab (Video-Pipeline) |
| `content/tools/` | Reel-Bau, Social-Posting, Token-Helfer, Analyse (17 Python-Tools plus Konfig) |
| `content/ads/` | Fertige 9:16-Reels und Ad-Creatives |
| `content/aban/` | „aban news Pro" – eigenständiger Newsletter (Engine, Worker, Landing) |
| `content/brand/` | Logo, Profil- und Titelbilder |
| `content/*.md` | Anleitungen, Posting-Pläne, Handoffs an Browser-Sessions |
| `snippets/luxe-*.liquid` | Storefront-Snippets für das Shopify-Theme (E-Mail-Popup, Trust-Strip) |
| `snippets/tiktok-pixel-luxestyle-ch.html` | TikTok-Pixel für den luxestyle.ch-Storefront – **nicht** ins Dashboard einbauen |
| `.github/workflows/` | Geplante Jobs: Social-Autopilot und aban-news-Versand |
| `.mcp.json` | Browser-Automation (Playwright MCP) für Cloud-Sessions |
| `CLAUDE.md` | Projekt-Memory / Entwickler-Notizen – die ausführliche Fassung |

## Automation

Unter `.github/workflows/` liegen geplante Jobs für das organische Posten
(Telegram, TikTok, Instagram, Threads, Facebook) und den täglichen
aban-news-Versand. Sie laufen nur, wenn die jeweiligen Secrets gesetzt sind –
fehlt ein Token, wird der Kanal sauber übersprungen statt zu scheitern.

**Zugangsdaten gehören nie ins Repo.** Tokens werden als GitHub-Secrets bzw.
Umgebungsvariablen gesetzt; die Tools lesen sie von dort.

## Deploy

Netlify published das Repo-Root direkt – es gibt kein Build-Kommando, nur die
Functions werden mit esbuild gebündelt (siehe `netlify.toml`). Gearbeitet wird
auf `main` plus kurzlebigen Feature-Branches, Änderungen laufen über Pull Requests.

Details, Konventionen und der aktuelle Projektstand stehen in
[`CLAUDE.md`](./CLAUDE.md); offene Punkte in [`TODO_ABEND.md`](./TODO_ABEND.md)
und [`STATUS_REPORT.md`](./STATUS_REPORT.md).
