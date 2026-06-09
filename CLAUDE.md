# LuxeStyle Dashboard — Projekt-Memory

Internes Single-Page-Dashboard für den Dropshipping-/Mode-Shop **LuxeStyle**. Statisches
HTML/CSS/JS, kein Build-Step, Deploy über Netlify.

## ⚠️ Offene To-dos / Sicherheit (ZUERST LESEN · Stand 2026-06-02)
- [ ] **TikTok-Access-Token rotieren** — wurde im Chat exponiert (Token + Advertiser-ID `7646349875793182738`). Neuen Token mit Scope **Creative Management** generieren (sonst Upload-Fehler 40001).
- [x] **DSers-Mapping gefixt** (2026-06-03): 18K Gold-Set → echter Lieferant **DIEYURO 316L Set** (Gold=B612, Silver=N1725), Cost ~CHF 1.75–3.95. Anleitung: `content/DSERS_MAPPING_FIX.md`.
- [x] **Counterfeit-/IP-Risiko:** Herren Sommer-Set (POLO), Gym-Shirt (Superman), Tracksuit (Wasserzeichen) **archiviert** (2026-06-03). Restliches Herren-Apparel noch sichten.
- [x] **US/Summer published** (Onlineshop+TikTok, 2026-06-03): Rain Cloud Diffuser · Sunset Lamp · **18K Gold-Set** (nach DSers-Fix) — alle live & kaufbar.
- [ ] **Ohrring-Set-Preis** = CHF 22.90 (nicht 29.90) — in Creatives korrekt halten.
- [ ] TikTok-Kampagne `luxestyle.ch`: Optimierungsereignis **Complete Payment** aktivieren + Creatives veröffentlichen.
- [ ] **Meta/IG-API geparkt (2026-06-04, „später holen"):** IG-Reel-Posting per Graph-API steht **kurz vor fertig**, hängt nur an **EINER** Sache: die Developer-App (`developers.facebook.com`) lässt sich **nur als persönliches Facebook „Alleng Chour"** erstellen — **NICHT** als das Business-Konto **„Luxestyle.ch FromPool"** (`allengchour@gmail.com`), mit dem man standardmäßig drin ist (→ „You don't have access" / „Create app" ausgegraut). **Resume:** komplett ausloggen → nur als **Alleng Chour** (persönl. FB) einloggen → developers.facebook.com → Create App (Business) → App-ID+Secret → `get_open_token.py meta` → `IG_ACCESS_TOKEN`+`IG_USER_ID` als GitHub-Secrets → `instagram_post.py` läuft. **Voraussetzung schon erledigt:** IG **@luxestyle.ch ist mit FB-Seite „LuxeStyle CH" verknüpft** (2026-06-04). ⚠️ Token NIE in den Chat (rotieren-To-do).
- [x] **TikTok-Ad-Ablehnung diagnostiziert (2026-06-04):** 2 Gründe — (1) **„Adult Supplies/Services" (CH)** = Fehlalarm, vermutlich zu viel Haut/Bademode/Model-Close-ups → produktfokussierte Creatives nutzen + Einspruch „fashion brand"; (2) **„Counterfeit" (US/GB/FR…)** = Marken-Look-Produkt (wahrsch. **Pandora-artiges Charm-Armband**, „anlauffrei"-Post) → Produkt entfernen/ersetzen, Fotos ohne Logos. Fix-Creatives gebaut: `content/ads/LuxeStyle_AdClean_*.mp4` (6×, produktfokus, keine Haut/Claims/Marken-Look) via `tools/build_ad_clean.py`.
- [ ] **Meta-Pixel LuxeStyle CH** = `1676528663551701` (Conversion-Tracking, NICHT Posting). TikTok-Pixel `D8EQE4JC77UAEKHUJCM0` meldet **Missing events** (Page view/Add to cart/Purchase fehlen) → Events Builder/Custom Code nachziehen.

### Session-Update 2026-06-05 (organisches Posten, Token, Ad-Ablehnung, Brand-Assets)
- **KOMMUNIKATIONS-PRÄFERENZ (User):** In Assistant-Antworten **KEINE Emojis** verwenden. (Emojis im Produkt/Shop/Collection-Titeln sind ok.)
- **Organisches Auto-Posten gebaut & live, aber blockiert durch fehlenden Token:**
  - `content/tools/threads_post.py` (NEU) = Threads-API (`graph.threads.net`, Container→Status→publish, Video/Foto/Text). 4. Kanal in `post_next_reel.py` (Telegram+TikTok+Instagram+Threads). Workflow `.github/workflows/luxestyle-social.yml` ist **auf `main` aktiv & geplant** (cron 2×/Tag 10:00/17:00 UTC = 12:00/19:00 CH) + `workflow_dispatch` (Input `index` = Reel aus `captions.json`). Postet automatisch, **sobald** ein gültiger Token gesetzt ist.
  - **WICHTIG App-Secret ≠ Access-Token:** Mehrere Fehlversuche, weil im Secret der **App-Geheimcode** (32 Hex, z.B. `b3bbb…`) statt eines **Access-Tokens** lag → Meta: `code 190 "Cannot parse access token"`. Echter Token = lang (100+ Zeichen). **Immer vorher im Token-Debugger prüfen** (`developers.facebook.com/tools/debug/accesstoken/`), erst dann ins Secret.
  - **Secrets-Status:** `IG_ACCESS_TOKEN` enthält aktuell einen **ungültigen** Wert; `THREADS_ACCESS_TOKEN`/TikTok/Telegram **nicht gesetzt**. Workflow hat Fallback `THREADS_ACCESS_TOKEN || IG_ACCESS_TOKEN`.
  - **Threads-Konto @luxestyle.ch war 2026-06-05 gesperrt** (suspended), Einspruch → wieder **online**. Token bleibt offen = **Laptop-OAuth-Job** (`threads.net/oauth/authorize?client_id=<THREADS_APP_ID 27222757947358241>&redirect_uri=https://luxestyle.ch/&scope=threads_basic,threads_content_publish&response_type=code` → Code → `get_open_token.py threads`).
  - **Grenze:** Claude Code kann **nicht selbst posten** (kein Konto-Login, kann Secrets nicht lesen). Zuverlässig = **manuell** (Reels liegen in `content/ads/`, Captions in `captions.json`). Per API nur, wenn gültiger Token als GitHub-Secret gesetzt ist.
- **TikTok-Ad-Ablehnung — ECHTER Grund (2026-06-05):** „Adult content" wegen **Text** in der Anzeige: **„69%"** und **„TURDAY"** (aus „Saturday") werden als veiled sexual references geflaggt (Region CH). **Fix = diese Strings entfernen** (keine „69"-Zahl, Wochentage ausschreiben/weglassen) → neu einreichen. **NICHT** Bademode/Landing-Page. Gilt generell: Zahlen/Wörter meiden, die als Anspielung lesbar sind.
- **Brand-Assets erstellt (`content/brand/`):** `LuxeStyle_Profilbild.png` (+ `_rund.png`, 1080²) & `LuxeStyle_AppIcon_1024.png` (Taupe/Cream Wordmark + LS-Monogramm) — für Social-Profile + Meta-App-Symbol.
- **Shop aufgeräumt (2026-06-04/05):** Collection **„Strand & Bademode"** (`strand-bademode`) angelegt → Bademode bleibt verkaufbar, aber **aus Ads raushalten** (Adult-Flag kommt vom Ad-Creative/Text, nicht vom Katalog). 2 Strand-Cardigans reaktiviert (ACTIVE). Polka-Dot-Kleid „Daisy" umbenannt (Deep-V-Wording raus).
- **Bios** für IG/TikTok/Threads/Facebook geschrieben (DE, mit `WELCOME10` + `luxestyle.ch`) — User trägt sie manuell ein.

### Session-Update 2026-06-05 (Teil 2 — Posting LIVE auf Threads/IG/FB, IDs)
- **Posten per API funktioniert jetzt real** (über kurzlebige Graph-Explorer-Token bzw. Threads-Long-Lived-Token, die der User generiert und in den Chat gibt; Claude tauscht/postet lokal):
  - **Threads:** live gepostet (Reels + Bilder). Threads-App-ID `27222757947358241`. Threads-User-ID `27478723925090794`.
  - **Instagram:** IG-Business-ID **`17841480560863361`** (@luxestyle.ch). Reels via `video_url`, Bilder via `image_url` (Graph API `/{ig}/media` → `media_publish`). Scope `instagram_content_publish`.
  - **Facebook-Seite LuxeStyle CH = ID `1049840534888592`.** Posten braucht **`pages_manage_posts`** (NICHT `pages_manage_metadata`!). Reel via `/{page}/videos file_url`, Fotos via `/{page}/photos url`. Seiten-Token aus `/me/accounts`.
- **MEDIEN-HOSTING (wichtig):** Repo ist **privat** → GitHub-Raw-URLs gehen NICHT für Threads/IG/FB. **Öffentliche Shopify-CDN-URLs nutzen.** Fertige 9:16-Ad-Videos liegen auf der CDN (siehe `content/shopify-product-videos.json`, Typ `fertige-ad-9:16`). **Bilder müssen JPG sein** (kein WebP) für Threads/IG.
- **Autopilot:** `content/tools/threads_auto_image.py` + Workflow `luxestyle-threads.yml` (2×/Tag auf `main`) postet rotierend 9:16-Reels (CDN) + Produktbilder. **Läuft selbst, sobald `THREADS_ACCESS_TOKEN` als Secret gesetzt ist** — Claude kann Secrets NICHT schreiben und Token NICHT anzeigen (Sicherheitsblock), dieser eine Schritt bleibt User-Hand.
- **Brand-Assets öffentlich auf Shopify-CDN** (für Handy-Download/Profile): `…/files/LuxeStyle_FB_Titelbild.png` + `…/files/LuxeStyle_Profilbild.png`. FB-Titelbild = `content/brand/LuxeStyle_FB_Titelbild.png`.
- **3–4 doppelte FB-„luxestyle"-Seiten** (IDs 2753403131698821, 1009159934884793, 1489200295389447) — **echte = LuxeStyle CH `1049840534888592`**. Duplikate später zusammenlegen/löschen (sonst zersplittern Follower; User sieht Posts „nicht", weil er Doppel-Seite ansieht).
- **Counterfeit-Risiko:** „**PureMax**"-Reel (Ohrringe, Fremdmarke) auf IG-Profil → entfernen (IG-Graph-API kann Posts NICHT löschen → manuell in der App).
- **Video-Qualität (User-Feedback):** Reels **flüssiger** bauen — Standbild in 2× Auflösung, **linearer Zoom (kein setpts-Slow-Mo)**, 30 fps. „Schlottert" sonst.
- **get_open_token.py threads** = kompletter OAuth (auth_code → short → long). Threads-**Tester** muss in App-Rollen hinzugefügt + via Instagram angenommen werden, sonst „user has not accepted the invite".

### Session-Update 2026-06-05 (Teil 3 — Katalog-Audit, Theme-Zugriff, Posting-Resultate)
- **Posting-Resultate (live):** Threads = 5 Produkt-Bilder + Reels live. Instagram = Reel + 5 Produkt-Bilder live (z.B. `instagram.com/p/DZN0nRtk0Im/`). Facebook-Seite LuxeStyle CH = 1 Reel + 5 Fotos live (über Token mit `pages_manage_posts`). User sah Posts „nicht", weil er **Doppel-FB-Seiten** ansah → echte Seite `1049840534888592`.
- **Katalog-Audit (Bulk-Export `bulkOperationRunQuery`):** **530 aktive** Produkte, **4 384 archiviert**. **0 exakte Titel-Duplikate.** Nur 5 milde „ähnlich"-Cluster (16 Produkte: 4 Diffuser, 3 Jade-Roller, 3 LED-Lampen, 3 S925-Halsketten = versch. Designs, 3 Bausteine-Sets = versch. Modelle) — das ist **echte Vielfalt, kein Dup**. **Entscheidung: Katalog/Collections NICHT anfassen.**
- **„Wirkt doppelt"-Gefühl** kommt vom **selben Produkt in mehreren Collections** (normal). Shopify kann **nicht** pro Collection ein anderes Bild zeigen (Vorschaubild ist produkt-level). **Fix = Theme-Toggle „Zweites Bild bei Hover anzeigen"** (Produktkarten → Medien) — User hat aktiviert. ~75-80 % der Produkte haben ein 2. Bild (Hover greift).
- **THEME-ZUGRIFF (wichtig für nächste Session):** Shopify-Anbindung kann Themes **lesen** + **unveröffentlichte (Draft-)Themes schreiben**, aber das **LIVE/MAIN-Theme ist gesperrt** (Sicherheits-Guardrail, nicht aufhebbar). Themes: **„Horizon · LuxeStyle Branded" = LIVE/MAIN (gesperrt)**; Drafts editierbar: „Horizon", „Horizon-Polish-Grid", „Horizon · LuxeStyle + Highlights (Preview)". **Workflow für Theme-Änderungen:** Live-Theme duplizieren → Claude editiert die Kopie (`themeFilesUpsert` auf Draft) → User klickt Vorschau → Veröffentlichen.
- **User-Vorgaben (2026-06-05):** Keine doppelten Bilder/Videos posten (Abwechslung). Reels **vorerst NICHT** neu bauen (genug Material) — wenn, dann **flüssiger** (2× Standbild, linearer Zoom, 30 fps). TikTok später. Follower **manuell** suchen (Auto-Follow = Policy-Verstoß/Sperr-Risiko, abgelehnt). „Regelmäßig automatisch überall posten" = braucht den THREADS_ACCESS_TOKEN-Secret-Schritt; sonst Posten auf Zuruf in varierten Batches.
- **FB-Seiten-Audit:** LuxeStyle CH `1049840534888592` (0 Fans, 16 Posts, IG-verknüpft) = behalten. **ABAN `111294918960305` = andere Marke (51 Fans), NICHT anfassen.** Doppel-„luxestyle"-Seiten nur **manuell** in Meta Business Suite löschbar (nicht per API).

### HANDOFF für neue Session (Stand 2026-06-05 Abend) — ZUERST LESEN
- **Tokens sind NICHT persistent:** Der Threads-Long-Lived-Token lag nur in `/tmp` dieser Session (jetzt weg). IG/FB-Graph-Explorer-Token sind kurzlebig (~1–2 h, abgelaufen). → **Neue Session hat KEINE gültigen Tokens.** Posten per API erst nach erneuter Token-Erzeugung durch den User: Threads via OAuth (`get_open_token.py threads`); IG+FB via Graph API Explorer mit Scopes `instagram_content_publish` + `pages_manage_posts` (+ `pages_show_list`). Token kommt vom User in den Chat, Claude tauscht/postet lokal per `urllib`.
- **DER eine nachhaltige Schritt:** `THREADS_ACCESS_TOKEN` als GitHub-Secret setzen → Autopilot `luxestyle-threads.yml` (2×/Tag) postet von selbst Reels (CDN) + Produktbilder. **Claude kann das Secret NICHT setzen (kein Tool) und Token NICHT anzeigen (Sicherheitsblock)** → einmalig User-Hand. Danach kein Token-Gejongliere mehr.
- **Heute (06-05) bereits gepostet — NICHT doppeln:** Threads ~15 (Reels + viele Sommer-Kleider/Produkte), Instagram ~10 (Reel + Produkte), Facebook ~6 (Reel + Fotos). Konten sind frisch/teils neu (Threads war gesperrt) → **Posting-Tempo drosseln** (Spam-/Sperr-Risiko). Lieber Autopilot-Drip 1–2/Tag statt Massen-Posts.
- **WebP→JPG nötig:** Top-Bestseller (Uhr, Diffuser, Jade-Roller, Galaxy-Projektor, Salzlampe, Wireless-Charger …) haben **WebP**-Bilder → IG/Threads lehnen WebP ab. Erst nach JPG-Konvertierung postbar: Shopify **staged upload** (`stagedUploadsCreate` → curl PUT → `fileCreate` → poll url) ergibt öffentliche CDN-JPG-URL. Für den Autopilot-Pool nach und nach konvertieren. (JPG-Apparel/Dresses gehen direkt.)
- **Theme:** „Zweites Bild bei Hover anzeigen" ist **aktiviert** (User, 06-05). Katalog = **530 aktiv / 4 384 archiviert, 0 exakte Duplikate** → **unangetastet lassen**. Theme-Änderungen nur auf Draft-Theme (Live „Horizon · LuxeStyle Branded" gesperrt) → User veröffentlicht.
- **Offene MANUELLE User-To-dos:** (1) `THREADS_ACCESS_TOKEN`-Secret setzen; (2) Doppel-FB-Seiten in Business Suite löschen (LuxeStyle CH `1049840534888592` behalten, ABAN nicht); (3) PureMax-Reel auf IG löschen.
- **Reels:** vorerst **pausiert** (genug Material). Nächste Charge **flüssiger** (2× Standbild, linearer Zoom, 30 fps, kein Slow-Mo).

### Session-Update 2026-06-09 (Browser-Automation/MCP — live getestet, GETEILT für alle)
- **Browser im Container funktioniert** (live verifiziert): Playwright/Chrome rendert `luxestyle.ch` als Full-Page-Screenshot. Pipeline end-to-end bewiesen, NUR der TLS-Handshake brauchte einen Fix (siehe Proxy).
- **Setup-Erkenntnisse (für JEDE Session, die einen Browser will):**
  1. **Netzwerk = Full** ist auf dieser Umgebung gesetzt (Chrome-Download lief). Default „Trusted" würde blocken.
  2. **Chrome/Chromium ist NICHT vorinstalliert.** Ad-hoc: `npx -y playwright@latest install --with-deps chrome` (oder `chromium`). Dauerhaft/gecacht: Inhalt von `scripts/install_browser.sh` ins **Setup-script-Feld der Umgebung** kopieren.
  3. **Security-Proxy bricht TLS** (eigene CA `swp-ca-production.crt`, `NODE_EXTRA_CA_CERTS`/`SSL_CERT_FILE` gesetzt) → Chrome wirft `ERR_CERT_AUTHORITY_INVALID`. **Fix = Browser mit `--ignore-https-errors` starten** (steht jetzt in `.mcp.json`). CLI-Demo: `npx -y playwright@latest screenshot --ignore-https-errors --full-page <url> out.png`.
  4. **MCP-Server lesen Config NUR beim Session-Start** → `.mcp.json`-Änderungen greifen erst in einer **frischen** Session, nicht mitten drin.
- **Dateien dieser Session (fertig im Arbeitsbaum):** `.mcp.json` (Playwright MCP, headless/isolated/ignore-https-errors), `scripts/install_browser.sh`, `content/tools/BROWSER_MCP_SETUP.md` (volle Anleitung + Browserbase-Block), `.gitignore`-Ergänzung, dieser Memory-Eintrag.
- **BLOCKER (wichtig für nächste Session):** Der Auto-Mode-**Sicherheits-Klassifizierer blockiert `git commit`/`git push`** für dieses Paket (wertet `.mcp.json`/Install-Skript als „Agent-Selbst-Modifikation/Persistenz"), AUCH wenn der User zustimmt. → Persistieren geht nur, wenn der **User die git-Freigabe im Cloud-UI erteilt** (Permission-Prompt / Berechtigungs-Modus / Bash-Permission-Regel). Bis dahin bleiben die Dateien uncommittet im Arbeitsbaum. NICHT über andere Tools (z. B. GitHub-MCP) um die Sperre herumrouten.
- **Einsatz:** risikoarm = öffentliche Web-Tasks (Recherche, Screenshots, **Checkout-Test luxestyle.ch**). Riskant = eingeloggtes Social-Posten (ephemer/2FA/Anti-Bot/ToS — nur mit Browserbase-Persistenz + bewusst).

## 🎯 Aktueller Stand & Fokus (für die nächste Session · 2026-06-03)
- **Fertige Reels liegen in `content/ads/`** (alle 9:16, CHF, ad-/postbar):
  `LuxeStyle_Mix_Reel_Sommer.mp4` (EU-Mix, 9 Produkte) · `LuxeStyle_EU_Hero_Reel.mp4` (Gold-Set+Diffuser+Lampe) ·
  `LuxeStyle_Herren_Reel.mp4` · `LuxeStyle_TikTok_AD_Sommer2026.mp4` (PRO mit Hook+Social-Proof).
- **Reel-Tools:** `content/tools/build_reel.py` (v3, Shopify-Auto + A/B), `tiktok_upload.py`, `get_token.py`. Doku `content/tools/README.md`.
- **🎯 User-Fokus JETZT = erster Kunde** (User-Vorgabe „warten, zuerst 1 Kunde haben"): **nicht mehr Reels bauen**, sondern:
  1. **Ein** Reel **organisch** auf TikTok posten (Trending-Sound + Link in Bio), 1×/Tag dranbleiben.
  2. **Warmes Netzwerk** (WhatsApp/Story) + Code `WELCOME10`.
  3. **Checkout selbst testen** (CH-Adresse, Pixel feuert?).
  4. Bezahlte Ad erst, wenn TikTok-Token (Scope Creative Management) steht — Upload via `tiktok_upload.py` ODER MP4 manuell in `ads.tiktok.com` ziehen.
- **US-Hero-Reel offen:** erst in DSers die **Supplier-Fotos** der 3 Hero-Produkte → Shopify pushen (`content/DSERS_MAPPING_FIX.md`), dann „US-Reel bauen" (Multi-Bilder, ggf. USD).
- **Posten/Ads/DSers/TikTok-Portal = NICHT per API für Claude Code** → Browser-Claude / User-Hand.


## ⚖️ TikTok-Ad-Compliance (ZUERST LESEN bei Reels/Ads · Stand 2026-06-03)
**Kontext:** Eine TikTok-Ad wurde abgelehnt („Review not approved · ad creatives rejected"). Diese Regeln **immer** einhalten, damit Creatives durchkommen — gilt für `build_reel.py`, `auto_cycle.py` und jede Ad:
- **KEINE unbelegten Bewertungs-/Sterne-Claims** im Video (z.B. „5.0 ★", „Über 50 Bewertungen", „56 Reviews"). Social-Proof-Karte nur mit **belegbaren** Zahlen — im Zweifel weglassen. (Default-Social-Proof wurde aus `build_reel.py` entfernt; `auto_cycle.py` baut keine Claim-Karte mehr.)
- **KEINE Health-/Wirkungs-Claims**: „anlauffrei", „hypoallergen", „wasserfest", „Anti-Aging", „anti-bakteriell" etc. → raus aus Captions/Karten.
- **KEINE restricted Produkte in Ads**: Beauty mit Wirkversprechen (Anti-Aging-Serum, Wimpernserum, Augencreme), Health/Medical. Im `product_pool.json` mit `"ad_restricted": true` markiert → `auto_cycle.pick_mix` überspringt sie.
- **Rabatt nur wenn echt aktiv**: `WELCOME10` muss im Shop wirklich gelten (tut es). „-10%" sonst weglassen.
- **Keine Fremdmarken/Logos/Wasserzeichen** im Bild (Lieferantenfotos prüfen) — Markenrecht.
- **Landing Page muss matchen**: Preis in Ad = Preis im Shop, Seite lädt, Impressum + Rückgabe/Kontakt vorhanden.
- **Saubere Optik, wenig Text**, kein „shocking/before-after", keine reißerischen Claims.
- **KEINE als Anspielung lesbaren Zahlen/Wörter** (TikTok-Ablehnung 2026-06-05 „Adult content"): konkret **„69%"** und **„TURDAY"** (aus „Saturday") wurden als veiled sexual references geflaggt. → Statt „69%" andere Rabattzahl nehmen; Wochentage/Wörter, die zerschnitten anstößig wirken, ausschreiben oder weglassen. Gilt für Anzeigentext UND eingebrannten Video-Text.
- **Musik**: nur lizenzfreier eigener Bed / Commercial Music Library (kein Trending-Pop in Paid Ads). Unser synthetischer Bed = ok.
- **Bei Ablehnung**: pro Creative den **genauen Grund** im Ads Manager lesen (Ad-Ebene) + **Appeal/Einspruch** (oft im 2. Durchgang frei). Ad-Sachen laufen über User-Hand/Browser-Claude.
- **Ad-safe Beispiel-Reels** (ohne Claims, nur Produkt+Preis+Code): `content/ads/LuxeStyle_Sommer_AdSafe.mp4` · `LuxeStyle_Geschenke_Ihn_AdSafe.mp4`.

## Wichtigste Fakten
- **Eine Datei zählt:** `index.html` enthält praktisch das gesamte Dashboard (HTML + CSS + JS inline).
- **Kein Backend für eigene Daten** → alle benutzerpflegbaren Daten liegen im **`localStorage`** des Browsers.
- **Zwei separate Shops:**
  - `luxestyle.com.co` — Haupt-Shopify-Shop (Pixel `D85BAGJC77UF23S9UDH0`, im Settings-Tab geführt).
  - `luxestyle.ch` — separater Shop für die TikTok-Sommer-Kampagne (eigenes Pixel `D8EQE4JC77UAEKHUJCM0`,
    Snippet in `snippets/tiktok-pixel-luxestyle-ch.html`). Diese beiden NICHT verwechseln.
- **Sprache der UI:** Deutsch (Schweiz). Neue Creator-/Kunden-Texte gibt es oft zusätzlich auf Englisch.

## Dateien
- `index.html` — Dashboard (Tabs, Logik). **Hier passiert fast alles.**
- `netlify/functions/shopify-oauth-callback.js`, `shopify-proxy.js` — Shopify-Anbindung (nur Shopify, nichts Eigenes).
- `netlify.toml` — Build/Headers. `tiktok_videos.json` — Quelle für den Content-Tab (Video-Pipeline).
- `snippets/tiktok-pixel-luxestyle-ch.html` — TikTok-Pixel-Code für den luxestyle.ch-Storefront (NICHT ins Dashboard einbauen).

## Tabs (`index.html`)
`overview` (Cockpit) · `products` (Shop) · `marketing` · `affiliate` · `pipeline` · `launchpad` · `stats` · `content` · `settings`.
Tab-Wechsel über `showTab(event, 'id')`. Für Sprung-Links aus anderen Tabs: `showTab(null, 'id')`.

## Selbstgebaute Module & ihre localStorage-Keys
| Modul | Tab | localStorage-Key | Render-/Init-Funktion |
|---|---|---|---|
| Affiliate-Programm + Creator-Tracking | `affiliate` | `luxe_affiliate_v1` | `affInit` / `affRenderCreators` |
| Kampagnen-To-do (Sommer) | `marketing` | `luxe_campaign_v1` | `campInit` / `campToggleStep` |
| E-Mail-Flow-Setup-Checkliste | `marketing` | `luxe_email_v1` | `emailInit` / `emailToggleStep` |
| Automation-Mails (8×, DE/EN) | `marketing` | `luxe_mail_v1` (+ `luxe_mail_lang_v1`) | `mailRender` |
| TikTok-Kommentar-Antworten (17×, DE/EN) | `content` | `luxe_tt_replies_v1` (+ `luxe_tt_lang_v1`) | `ttReplyRender` |
| Mode-Creatives (8×, DE/EN) | `content` | `luxe_creative_v1` (+ `luxe_creative_lang_v1`) | `creativeRender` |
| Kundenservice-Antworten (DE/EN) | `marketing` | `luxe_service_v1` (+ `luxe_service_lang_v1`) | `serviceRender` |
| Cockpit-Übersicht (aggregiert) | `overview` | — (liest die obigen) | `cockpitRender` |

Alle Render-Funktionen werden am Ende des Haupt-`<script>` initial aufgerufen (Block direkt vor `</script>`).

## Konventionen / Muster
- **Globale Funktionen**, inline `onclick="..."` als Event-Verdrahtung (kein Framework, kein Bundler).
- HTML wird per String-Konkatenation gebaut. Beim Einsetzen von User-/Default-Text in HTML
  `affEsc(text)` zum Escapen nutzen (existiert im Affiliate-Block).
- Bilinguale Module: Daten-Array mit `{ de: ..., en: ... }`, Sprach-Toggle-Buttons mit
  eigenem `data-*lang`-Attribut, Auswahl + Edits getrennt pro Sprache in localStorage.
- Wiederverwendbare CSS-Klassen: `.section`, `.section-header`, `.section-subtitle`, `.section-title`,
  `.kpi-grid`/`.kpi`, `.grid-2`, `.profit-card`/`.profit-row(.total/.profit)`, `.table`,
  `.alert(-info/-success/-warning)`, `.btn`/`.btn-sm`/`.btn-primary`, `.ttf-btn(.ttf-active)`,
  `.tt-reply`, `.aff-input`/`.aff-cell`/`.aff-step`. Neues CSS sparsam, am besten in den bestehenden `<style>`-Block.
- `copyCode(text)` kopiert in die Zwischenablage (mit Alert-Bestätigung) — für alle 📋-Buttons nutzen.
- **Pixel/Tracking-Snippets gehören NICHT in `index.html`** (das ist das interne Admin-Tool, kein Storefront).

## Vor jedem Commit prüfen
JS-Syntax des Haupt-Skriptblocks validieren und Tag-Balance checken:
```bash
python3 - <<'PY'
import re
html = open('index.html', encoding='utf-8').read()
blocks = re.findall(r'<script>(.*?)</script>', html, re.S)
open('/tmp/main.js','w',encoding='utf-8').write(blocks[-1])
print('script blocks:', len(blocks))
PY
node --check /tmp/main.js
python3 -c "h=open('index.html').read(); print('divs:',h.count('<div'),h.count('</div>'))"
```
Erwartung: **3** Script-Blöcke (winziges Head-Theme-Init für Dark-Mode · Content-Tab · Haupt-Skript),
`node --check` ohne Fehler (prüft den letzten/Haupt-Block), `<div>`/`</div>` ausgeglichen.
Funktionaler Test: `index.html` im Browser öffnen — alles läuft client-seitig, Netlify nicht nötig.

## Git / Workflow
- Entwicklungs-Branch: `claude/blissful-albattani-wUQZV`. Push mit `git push -u origin <branch>`.
- **PR #1** (Affiliate · Kampagne · E-Mail-Flows · TikTok-Antworten · Creatives · Cockpit) ist **gemergt** (squash → `main`).
- **PR #2** (Draft) — Kundenservice-Antworten-Modul. Nach dem Push immer einen (Draft-)PR sicherstellen.
- **PR #20** (Ready for review) — Reel-/Ad-Pipeline + finale TikTok-Ad „Sommer 2026" (`content/ads/`, Handoff `BROWSER_CLAUDE_TIKTOK_AD.md`, Manifest/Rezepte in `content/`). Stand 2026-06-02.
- Footer-Versionsstring in `index.html` (Suche `class="footer"`) bei größeren Änderungen mitziehen.

## Externer Projekt-Stand (außerhalb des Repos · Juni 2026)
Läuft über In-Admin-Tools / MCP, NICHT im Dashboard-Code:
- **Shopify** (`luxestyle.ch`, CHF · Markets: **USA = USD aktiv**): 5 Produkte „US/Summer 2026" live mit
  Bild + Varianten + Dropship-Inventar (SKUs `LX-DIFF/LAMP/CLOCK/PHN/JWL`), Collection „US / Summer 2026".
  Echte Dropship-Produkte kommen über **CJ/DSers** (echte Fotos + Lieferanten-SKUs, z. B. Ring, Shorts).
- **Klaviyo** (Account = LuxeStyle CH, hängt am `.com.co`-Shop): **14 E-Mail-Templates** (7 DE + 7 EN:
  Cart 1–3, Welcome 1–2, Post-Purchase, Win-Back), Branding Taupe/Cream, Code `WELCOME10`.
  Flows müssen in der Klaviyo-UI gebaut/aktiviert werden (API kann keine Flow-Trigger anlegen).
- **Loox:** 56 Reviews (5.0★) importiert, Core-Script im Theme aktiv.
- **TikTok Ads** (`luxestyle.ch`): Kampagne „LuxeStyle Mode CH – Sommer" als Entwurf; Pixel
  `D8EQE4JC77UAEKHUJCM0` aktiv. Offen: Optimierungsereignis **Complete Payment** + 4 Creatives → veröffentlichen.
- **Nur In-Admin (keine API für Claude):** DSers, Loox, TikTok/Meta Ads.
- **Bild-Lektion:** Shopify-Produktbilder müssen **< 25 MP** sein, sonst Fehler „Mediendatei konnte nicht
  verarbeitet werden". Adobe-Stock-**Free**-Collection taugt für Platzhalter (0 Credits, kommerziell nutzbar) —
  große Assets (>25 MP) vorher herunterskalieren (z. B. `image_crop_and_resize`).

## 🎨 Brand-Bildsprache (WICHTIG — User-Vorgabe)
Visuals/Reels: **premium, clean, lifestyle, Fokus aufs Produkt.** **Vermeiden:** billig wirkende Generic-Stock-Clips
(Massen-Schuhe/Brillen/Kleider, generische Model-Stockclips) — alles, was nach Billig-Dropshipping aussieht.
Hochwertige, ästhetische Optik. (In `content/revid-render-payloads.json` als `stylePrompt` + `quality:ultra` hinterlegt.)

## 🎬 Content-/Reel-Automation (`content/`)
- `reels-schedule.csv` (14T) · `-30d.csv` · `-90.csv` (3×/Tag, Mix Herren/Schmuck/US/Tech) · `reel-posting-plan*.md`
- `revid-prompts.md` (Script-Prompts je Produkt) · `revid-render-payloads.json` (16 fertige v3-render-Payloads, Premium-Settings)
- `revid-api-usage.md` · `makecom-autopost-blueprint.md`
- `tools/build_reel.py` (v3) — **Automatisierungs-Tool**: JSON/CLI → fertiges TikTok-Premium-9:16-Reel/Ad. Features: **Shopify-Auto-Modus** (`--shopify handles` / `--shopify-query 'tag:..'` → zieht Titel/Preis/Bild per Admin-API, ENV `SHOPIFY_STORE`+`SHOPIFY_ADMIN_TOKEN`, überspringt nicht-published), **A/B-Hooks** (mehrere Varianten → `_A/_B`), **gratis DE-Voiceover** (Keys `voiceover`+`voice_model`, lokal via **piper-tts**, unter geduckte Musik gemischt — keine API/Credits; `pip install piper-tts` + `.onnx`-Stimme über `LUXE_PIPER_VOICE`), Hook-/Social-Proof-Karten, animierte Captions, Story-Progress-Bar, Preis-Badge, Musik-Moods, Markenfarbe. Cross-platform. Doku: `tools/README.md`.
- `tools/tiktok_upload.py` — lädt fertige Reels per **TikTok Marketing API** in den Ads Manager (Creative Library). ENV `TIKTOK_ACCESS_TOKEN`+`TIKTOK_ADVERTISER_ID`. `python tiktok_upload.py reel.mp4` (oder `--url`, `--list`). Pipeline: build_reel.py → tiktok_upload.py. `tools/get_token.py` holt den Access-Token (OAuth auth_code→token; braucht App-Scope **Creative Management**, sonst Fehler 40001).
- `tools/tiktok_campaign.py` — legt eine **komplette Anzeige** (Kampagne→AdGroup→Ad) per Marketing API an, statt im Ads Manager zu klicken. Defaults: Ziel **WEB_CONVERSIONS** (kein Katalog → kein `DpaAudienceTypeRender`-Fehler), **BID_TYPE_NO_BID** = Lowest Cost (kein Target-CPA → löst „Set a bid price"), Pixel `D8EQE4JC77UAEKHUJCM0`, Schweiz/DE+FR, CHF 20/Tag, **erstellt PAUSIERT** (`--live` für sofort). `python tiktok_campaign.py --video ../ads/LuxeStyle_Sommer_AdSafe.mp4` (lädt Video selbst hoch). Braucht Token-Scopes **Ads Management + Creative Management**.
- `tools/tiktok_analyze.py` — **TikTok-Performance-Analyse** öffentlicher Profile (Default `@luxestyle.ch`) **ohne API/Login** via `yt-dlp` → JSON+MD-Report (Views/Engagement, Top-Videos, Hashtag-Performance, beste Posting-Zeiten, Hook-Ranking). `pip install -U yt-dlp`; `python tiktok_analyze.py` (portiert aus aban-news, Default angepasst). Liefert Daten für Hooks/Posting-Plan.
- `tools/social_post.py` — **gratis Posten** (Reel via `--video` ODER Text) auf **Telegram** (sendVideo), Discord, generischer Webhook. Nur stdlib, kein Make/Zapier. ENV `TELEGRAM_BOT_TOKEN`+`TELEGRAM_CHAT_ID` (NIE im Chat — als Secret setzen!). `python social_post.py --video ../ads/LuxeStyle_EU_Hero_Reel.mp4`. Aus aban-news `social/post.py` erweitert (Video-Upload). **TikTok bleibt Hand-Upload** (kein offener Endpoint). **Bot existiert:** @LuxestyleCHbot (Token war im Chat exponiert → rotieren!).
- `tools/tiktok_post.py` + `tools/instagram_post.py` + `tools/get_open_token.py` + `tools/captions.json` + `.github/workflows/luxestyle-social.yml` — **organisches Posten auf TikTok-Profil + Instagram** (eigene stdlib-Tools, kein Make/Buffer). TikTok = **Content Posting API** (`open.tiktokapis.com`, Scope `video.upload`): `--draft` lädt ins TikTok-Entwürfe (1× in App posten, **kein Audit nötig**), `--direct` nach 2–4-Wochen-Audit. IG = **Graph API Reels** (Business-Konto + FB-Seite, Video als GitHub-Raw-URL). `post_next_reel.py` = Multi-Kanal-Rotation (Telegram+TikTok+IG, je nach Secret; sonst übersprungen). OAuth via `get_open_token.py`. ⚠️ Voll-auto öffentlich erst nach TikTok-Audit / IG-Business-Setup; Tracking-Pixel ≠ Posting-Token. Token als GitHub-Secret.
- `tools/product_pool.json` + `tools/auto_cycle.py` + `.github/workflows/luxestyle-auto.yml` — **Stunden-Automation**: rotiert je Lauf einen frischen Produkt-Mix aus dem Pool (echte published Shopify-Produkte, CHF) → baut Reel (`build_reel.py`) → **lernt** aus dem neuesten `tiktok_analyze`-Report (Top-Hashtags/Hook) → postet **Text-Status (KEIN Video)** auf Telegram. Reels = GitHub-Artefakt (nicht ins Repo), nur Lern-Report/Log wird committet. ⚠️ cron läuft **erst nach Merge nach `main`** (geplante Workflows nur auf Default-Branch); vorher per `workflow_dispatch`. Secrets `TELEGRAM_BOT_TOKEN`+`TELEGRAM_CHAT_ID` im Repo setzen. Takt via cron entschärfbar (`0 */3 * * *`).
- `shopify-product-videos.json` (17 echte Shop-Videos: 13 Produkt-Demos + 4 fertige 9:16-Ads, per Admin-API gefunden) · `revid-custom-media-recipe.md` (echte Fotos/Videos statt Stock via `media.type:custom`) · `reel-build-recipe-ffmpeg.md` (lokale 9:16-Montage; ffmpeg-Build **ohne drawtext** → Text als PNG-Overlay) · `reels-produced-2026-06.md` (Log)
- **Reel-Learnings (2026-06):** Für **produkttreue** Reels echte Shop-Assets nutzen (Stock = nur Lookalike). Flüssiger Ken-Burns = Standbild in 2×-Auflösung + linearer `zoompan` (kein `setpts`-Slow-Mo → ruckelt). Manche Demo-Clips zeigen Fremdmarken/Lieferantentexte → croppen. Ad-Kleider («Savanna», «Brise» …) sind KI-Ad-Konzepte → erst als echtes Produkt bestätigen.
- **Revid.ai:** Plan Growth ($39, 2 000 Credits). API `POST https://www.revid.ai/api/public/v3/render` (Header `key` oder `Bearer`), MCP `https://www.revid.ai/api/mcp`. Egress aus Sandbox funktioniert. **API-Key nötig** (im Revid-Konto erstellen). Generieren kostet Credits → klein starten.
- **Make.com:** Org 7603352 · Team 1667409 · Zone **eu1** (Verbindung flaky → Retries). Connections vorhanden: **Shopify, YouTube, Gmail, Buffer**. **Buffer** = Multi-Plattform-Posting (TikTok/IG/Threads/YT). API-Token authentifiziert, aber **OAuth-Connections + Szenario-Aufbau gehören in die Make-UI** (Browser-Claude). API-Key war im Chat exponiert → rotieren.
- **Browser-Automation (MCP) — `/.mcp.json` + `scripts/install_browser.sh` + `content/tools/BROWSER_MCP_SETUP.md`:** Damit Cloud-Sessions einen echten Browser steuern (Web ansteuern, Screenshots, Checkout-Test, ggf. eingeloggtes Posten). **Playwright MCP** (lokaler headless-Chromium, gratis) ist in `.mcp.json` aktiv; **Browserbase** (Cloud-Browser, persistente Logins, kostenpflichtig) ist im Setup-Doc als Copy-Paste-Block einschaltbar. ⚠️ **2 Schalter bleiben User-Hand** (nicht committbar): (1) Umgebungs-**Network access auf Full/Custom** — Default „Trusted" blockt Webseiten + Playwright-CDN → Browser bleibt sonst blind; (2) Chromium installieren (Setup-Skript-Feld der Umgebung **oder** SessionStart-Hook **oder** ad-hoc `bash scripts/install_browser.sh`); für Browserbase zusätzlich `BROWSERBASE_API_KEY`/`_PROJECT_ID` als Env-Var. **Grenzen:** Container ephemer → eingeloggte Sessions überleben nicht (Social-Posting nur mit Browserbase-Persistenz zuverlässig) + 2FA/Anti-Bot/**ToS-Sperr-Risiko** (Auto-Aktionen früher genau deswegen abgelehnt). Risikoarm/empfohlen = öffentliche Web-Tasks (Recherche, Screenshots, eigenen Checkout testen). Details: `content/tools/BROWSER_MCP_SETUP.md`.

## 🔗 Schwester-Repo `aban-news-landing` — Tools wiederverwenden (User-Freigabe)
Öffentliches Repo `allengchour-glitch/aban-news-landing` → **per `git clone` les-/nutzbar** (kein MCP-Scope nötig):
`git clone --depth 1 https://github.com/allengchour-glitch/aban-news-landing.git /tmp/aban`.
**Für LuxeStyle direkt nützlich (bei Bedarf adaptieren, ENV/Secrets bleiben raus aus Git):**
- `social/post.py` — **Mehrkanal-Publisher** (Discord/Telegram/Mastodon + generischer `PUBLISH_WEBHOOK_URL` → Make/n8n → LinkedIn/X/IG). Löst das „Posten"-Problem ohne native APIs.
- `video-prototypes/` (+ `XTTS-SETUP.md`) — lokales TTS-Setup. **Umgesetzt:** statt XTTS (zu schwer: 1.8 GB torch) → **piper-tts** gewählt & in `build_reel.py` integriert (`voiceover`-Key, gratis DE-Stimme).
- `tools/tiktok_analyze.py` — TikTok-Performance-Analyse. **Bereits nach `content/tools/tiktok_analyze.py` portiert** (Default `@luxestyle.ch`).
- `tools/daily_improvement_scan.py`, `tools/board.py`, `tools/link_checker.py`, `tools/brand-voice-linter.py` — Automations-/QA-Bausteine.
- `.github/workflows/*` — Muster für geplante GitHub-Action-Automationen (Build/Audit/Suggest).
