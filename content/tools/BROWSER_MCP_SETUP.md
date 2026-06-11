# Browser-Automation (MCP) — Setup & Nutzung

Damit künftige **Claude-Code-Cloud-Sessions** einen echten Browser steuern können (Webseiten ansteuern,
Screenshots, Formulare ausfüllen, Checkout testen, ggf. eingeloggtes Posten). Die Verdrahtung liegt im Repo;
**zwei Schalter** bleiben aber bei dir, weil sie nicht committbar sind (Netzwerk-Policy + ggf. API-Key).

> Kurz: `.mcp.json` aktiviert **Playwright MCP** (lokaler Browser im Container, gratis). **Browserbase**
> (Cloud-Browser mit persistenten Logins, kostenpflichtig) ist hier dokumentiert und mit einem Copy-Paste-Block
> einschaltbar.

---

## 1. Die 2 Schalter (User-Hand — ich kann sie nicht committen)

### Schalter A — Netzwerk auf "Full" oder "Custom" (PFLICHT)
Die Standard-Policy **"Trusted"** lässt nur Paket-Registries/GitHub zu — **keine** beliebigen Webseiten und nicht
den Playwright-Browser-Download. Ohne diesen Schalter bleibt der Browser blind.

- Cloud-Umgebung öffnen (Cloud-Icon → Umgebung → Bearbeiten) → **Network access**:
  - **Full** = einfachster Weg (jede Domain).
  - **Custom** = restriktiver; dann mindestens erlauben:
    - `cdn.playwright.dev`
    - `playwright.download.prss.microsoft.com`
    - die Ziel-Seiten, die der Browser besuchen soll (z. B. `*.luxestyle.ch`, `*.tiktok.com`, `*.facebook.com` …)
    - für Browserbase zusätzlich `*.browserbase.com`
    - Haken "Also include default list of common package managers" anlassen.

### Schalter B — Chromium installieren
Der Container hat Chromium nicht vorinstalliert. `scripts/install_browser.sh` erledigt das. Wähle **eine** Variante:

- **A) EMPFOHLEN — Setup script (gecacht, schnell):** Inhalt von `scripts/install_browser.sh` in das
  **"Setup script"**-Feld der Umgebung kopieren. Läuft einmal, Ergebnis wird ~7 Tage gecacht.
- **B) OPT-IN — SessionStart-Hook (läuft bei jedem Start):** Falls du Auto-Install bevorzugst, lege
  `.claude/settings.json` mit folgendem Inhalt an (bewusst von dir hinzugefügt):
  ```json
  {
    "hooks": {
      "SessionStart": [
        { "matcher": "startup|resume",
          "hooks": [ { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/scripts/install_browser.sh" } ] }
      ]
    }
  }
  ```
- **C) Ad-hoc:** in einer laufenden Session einfach `bash scripts/install_browser.sh` ausführen lassen.

### (nur für Browserbase) Schalter B2 — API-Key als Env-Var
Es gibt keinen Secret-Store. In der Umgebungs-UI unter Environment-Variablen setzen:
```
BROWSERBASE_API_KEY=bb_...
BROWSERBASE_PROJECT_ID=...
```
> Hinweis: Env-Vars der Umgebung sind für jeden sichtbar, der die Umgebung bearbeiten darf. Keys, die hier landen,
> entsprechend behandeln (rotierbar halten).

---

## 2. Was schon im Repo aktiv ist: Playwright MCP

`/.mcp.json`:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest", "--headless", "--isolated"]
    }
  }
}
```
- Offizieller Microsoft **Playwright MCP**. `--headless` (kein Display im Container), `--isolated` (frischer
  Browser-State je Session — passt dazu, dass Container ephemer sind).
- Nach Schalter A+B erscheinen in der Session Tools wie `browser_navigate`, `browser_take_screenshot`,
  `browser_click`, `browser_type`, `browser_snapshot` …

### Alternative ohne "Full"-Netzwerk (Trusted-freundlich)
Wenn du das Netzwerk eng halten willst und der Playwright-CDN nicht erlaubt werden soll: System-Chromium per apt
(Ubuntu-Archiv ist auch unter "Trusted" erlaubt) und Playwright darauf zeigen lassen.
Im Setup script statt `playwright install`:
```bash
apt-get update && apt-get install -y chromium-browser
```
und den MCP-Start in `.mcp.json` auf den System-Browser zeigen:
```json
"args": ["-y", "@playwright/mcp@latest", "--headless", "--isolated",
         "--executable-path", "/usr/bin/chromium-browser"]
```
(Die Ziel-Seiten müssen unter "Custom" trotzdem erlaubt sein.)

---

## 3. Browserbase einschalten (Cloud-Browser, persistente Logins)

Wann sinnvoll: wenn ein **eingeloggter** Zustand über die Session hinaus halten soll (das schafft der lokale
Playwright-Container wegen Ephemeralität nicht zuverlässig) oder du Stealth/Proxies brauchst.

`/.mcp.json` um diesen Server ergänzen (zusätzlich zu oder statt Playwright):
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest", "--headless", "--isolated"]
    },
    "browserbase": {
      "command": "npx",
      "args": ["-y", "@browserbasehq/mcp"],
      "env": {
        "BROWSERBASE_API_KEY": "${BROWSERBASE_API_KEY}",
        "BROWSERBASE_PROJECT_ID": "${BROWSERBASE_PROJECT_ID}"
      }
    }
  }
}
```
Voraussetzungen: Browserbase-Konto, Schalter A (Netzwerk inkl. `*.browserbase.com`), Schalter B2 (Keys).

---

## 4. Einsatzzwecke

### Risikoarm (empfohlen) — öffentliche Web-Tasks, keine Logins
- Konkurrenz-/Markt-Recherche, Preise scrapen, Trends ansehen.
- Screenshots von Landingpages/Produktseiten.
- **Eigenen `luxestyle.ch`-Checkout testen** (CH-Adresse durchspielen, prüfen ob das Pixel feuert) — offenes To-do.
- Öffentliche TikTok-/IG-Profile ansehen (ergänzt `tiktok_analyze.py`).
Kein Login, kein Sperr-Risiko. Hier liegt der zuverlässige Mehrwert.

### Riskant — eingeloggtes Posten/Klicken (TikTok-Ads-Manager, Meta Business Suite)
Technisch möglich, aber bewusst mit Vorsicht:
- **Ephemer:** Login/Cookies überleben keine Session → nur mit Browserbase-Persistenz halbwegs praktikabel.
- **2FA / Anti-Bot:** Plattformen blocken Automatisierung aktiv.
- **ToS-/Sperr-Risiko:** Automatisierte Aktionen auf Social-Konten können zu Sperren führen. Auto-Follow & Co.
  wurden im Projekt früher **genau deswegen** abgelehnt. → Nur bewusst und am besten manuell-assistiert (User schaut
  zu / bestätigt), nicht als unbeaufsichtigte Automation.

---

## 5. Verifikation (nach Schalter A+B, in einer **neuen** Cloud-Session)
1. Session starten → Chromium-Install-Log prüfen (`[install_browser] Chromium installiert.`).
2. „Navigiere zu https://luxestyle.ch und mach einen Screenshot" → `browser_navigate` + `browser_take_screenshot`
   müssen erscheinen und liefern.
3. Browserbase: Block + Keys + `*.browserbase.com` → erneut testen.

## 6. Bekannte Stolpersteine
- **Netzwerk "Trusted"** → Browser blind / Chromium-Download scheitert. Häufigster Fehler. Siehe Schalter A.
- **Security-Proxy:** ganzer Egress läuft über einen Proxy. Falls Playwright nicht rauskommt, `HTTPS_PROXY`/
  `HTTP_PROXY` an den Browser durchreichen.
- **Ressourcen:** Container hat ~4 vCPU / 16 GB RAM / 30 GB Disk — für einen headless-Browser ausreichend.
