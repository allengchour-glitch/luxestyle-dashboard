#!/bin/bash
# Installiert Playwrights Chromium fuer den Playwright-MCP-Server (.mcp.json).
#
# Aufruf (eine der beiden Varianten — siehe content/tools/BROWSER_MCP_SETUP.md):
#   A) EMPFOHLEN: Inhalt in das "Setup script"-Feld der Cloud-Umgebung kopieren
#      (laeuft einmal, wird gecacht -> schnelle Starts).
#   B) OPT-IN: per SessionStart-Hook in .claude/settings.json verdrahten
#      (laeuft bei jedem Start; der Hook muss bewusst vom User hinzugefuegt werden).
#   C) Ad-hoc: in einer Session einfach  bash scripts/install_browser.sh  ausfuehren.
#
# Wichtig:
#   - Nur in Cloud-Sessions (CLAUDE_CODE_REMOTE=true). Lokal macht das Skript nichts.
#   - Idempotent: ueberspringt die Installation, wenn Chromium schon vorhanden ist.
#   - Braucht Netzwerk "Full" oder "Custom" (Playwright-CDN ist NICHT in der
#     Trusted-Allowlist). Bei "Trusted" schlaegt der Download fehl -> klarer Hinweis.
#     Alternative ohne Full-Netzwerk: siehe content/tools/BROWSER_MCP_SETUP.md
#     (System-Chromium per apt + --executable-path).

set -u

# Lokal nichts tun (Browser nicht auf dem Laptop des Users installieren).
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Schon installiert? Dann fertig (SessionStart laeuft bei jedem Start).
CACHE_DIR="${PLAYWRIGHT_BROWSERS_PATH:-$HOME/.cache/ms-playwright}"
if ls "$CACHE_DIR"/chromium-*/ >/dev/null 2>&1; then
  echo "[install_browser] Chromium bereits vorhanden ($CACHE_DIR) - ueberspringe."
  exit 0
fi

echo "[install_browser] Installiere Playwright Chromium (+ System-Libs)..."
# --with-deps zieht die noetigen apt-Libs (Ubuntu-Archiv ist auch unter "Trusted" erlaubt);
# der Chromium-Binary-Download braucht aber Full/Custom-Netzwerk.
if npx -y playwright@latest install --with-deps chromium; then
  echo "[install_browser] Chromium installiert."
else
  echo "[install_browser] WARNUNG: Chromium-Install fehlgeschlagen."
  echo "[install_browser] Meist Ursache: Netzwerk steht auf 'Trusted' und blockt den Playwright-CDN."
  echo "[install_browser] Fix: Umgebung -> Network access auf 'Full' (oder 'Custom' mit"
  echo "[install_browser]      cdn.playwright.dev + playwright.download.prss.microsoft.com)."
  echo "[install_browser] Siehe content/tools/BROWSER_MCP_SETUP.md fuer die apt-Alternative."
fi

# Hook darf die Session nie blockieren.
exit 0
