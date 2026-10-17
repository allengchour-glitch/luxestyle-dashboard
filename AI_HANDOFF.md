# LuxeStyle – gemeinsame Übergabe ChatGPT / Claude
Stand: 2026-10-17. Diese Datei ist eine Projektübergabe, kein automatischer gemeinsamer KI-Memory-Speicher.

## Aktueller Betrieb
- Storefront: luxestyle.ch, Shopify ist das produktive Shopsystem.
- Betreiber hat Netlify gekündigt und nutzt kein Dashboard mehr. **Nicht** von aktivem Netlify-Deployment ausgehen.
- GitHub-Repository enthält historische Dashboard-, Netlify-, Social- und Aban-News-Arbeit. Nicht blind löschen.
- ChatGPT hat lesenden Zugriff auf Shopify, Metricool, Klaviyo und GitHub über verbundene Apps.
- **Keine ungefragten Live-Änderungen, Posts, Verkäufe, Rabattaktionen oder Deployments.** Sicherheitsfixes zunächst als Review-PR; Freigabe vor Merge und Deployment.

## Geprüfte Code-Befunde
1. `netlify/functions/shopify-proxy.js`: Token aus Netlify Blobs; keine eigene Benutzer-Authentifizierung; erlaubt auch schreibende HTTP-Methoden und Kunden-/Bestell-/Theme-Endpunkte. Kritisch, falls noch erreichbar. Zuerst Deployment-Status prüfen.
2. `netlify/functions/shopify-oauth-callback.js`: HMAC-Parameter wird nur gelesen, nicht verifiziert; kein state-Abgleich. Kritisch, falls noch aktiv.
3. `netlify.toml`: `publish = "."`; bei aktivem Deployment mögliche Veröffentlichung interner Repo-Dateien prüfen.
4. `.github/workflows/luxestyle-social.yml`: fehlende explizite `permissions: contents: read`; zweimal täglich geplant, kein dauerhafter Duplikat-Schutz.
5. `content/tools/post_next_reel.py`: Fehler einzelner Plattformen werden gesammelt, aber Skript beendet sich nicht mit Fehlercode. Daher kann GitHub Actions grün erscheinen trotz fehlgeschlagener Posts.
6. `CLAUDE.md`: früher offengelegter TikTok-Token als offener Rotationspunkt dokumentiert; Status aktuell unbekannt. Keine Tokens in Chat oder Repository kopieren.
7. `.github/workflows/aban-news.yml`: verarbeitet Abonnentendaten und hat `contents: write`; separat überprüfen. Gehört zu Aban News, nicht unmittelbar zu LuxeStyle-Verkäufen.
8. Shopify-API-Version `2024-10` im historischen Proxy veraltet. Nur relevant bei weiterer Nutzung.

## Klaviyo (letzte 30 Tage, abgefragt 2026-10-17)
- Flow `Vse76a` „Abandoned Checkout“ derzeit draft: 11 Empfänger, 9 Zustellungen, 1 zugeschriebene Bestellung, CHF 45.90 zugeschriebener Umsatz. Vergangene Aktivität kann vor Draft-Status erfolgt sein.
- Welcome `VbLQj6`: 3 zugestellt, 0 zugeschriebene Bestellungen.
- Post-Purchase `RnTvsY`: 2 zugestellt, 0 zugeschriebene Bestellungen.
- Aktueller Live-Checkout-Flow `XEGbTB`: keine Zeile im abgefragten Flow-Performance-Report; Trigger, Nachrichtenstatus und Ereignisse prüfen, nicht blind neue Flows aktivieren.

## Marketing / Umsatz
- Shopify-Abfrage für letzte 30 Tage: 1783 Sessions, 7 abgeschlossene Checkouts, 0,39 % Conversion (Zeitfenster und Attribution bei weiteren Analysen neu prüfen).
- TikTok/Metricool: 1.–4. Okt. 99'943 Videoaufrufe, 5.–8. Okt. 3'547; Einbruch der Reichweite. Nicht einfach Posting-Menge erhöhen; erfolgreiche Produkte, Produktseite und Tracking untersuchen.

## Priorisierte sichere Schritte
P0: Prüfen, ob historische Netlify-Funktionen tatsächlich offline sind. Falls aktiv, Zugriff sofort absichern; Tokens rotieren, falls exponiert.
P0: GitHub Secrets und Token-Gültigkeit ohne Offenlegung prüfen.
P1: Social-Workflow-Rechte minimieren, Fehlerstatus korrekt melden, Duplikat-Posts verhindern; PR ohne Auto-Merge.
P1: Klaviyo Checkout-Flow anhand Ereignissen und Message-Status testen, ohne live zu schalten.
P1: Shopify-Mobile-Checkout und Produktseiten kontrollieren, ohne Testkauf abzuschliessen.
P2: Alte Dashboard-/Netlify-Dateien erst nach Prüfung von Referenzen und Nutzungsbedarf archivieren; keine destruktive Bereinigung.

## Zusammenarbeit
- ChatGPT und Claude können diese Datei über GitHub lesen. Es gibt **keine** direkte gemeinsame Chat-/Memory-Synchronisierung.
- Nach wichtigen Änderungen diese Übergabe aktualisieren, Datum und konkrete PRs nennen.
- Keine personenbezogenen Daten, Zugangstokens, API-Secrets oder Kundendaten in Übergabedateien.
