# Facebook Page-Token (langlebig, nie ablaufend) + Posting

Ziel: Ein **Page-Token**, das **nicht abläuft**, damit die Facebook-Seite „LuxeStyle CH"
(ID `1049840534888592`) automatisch beposten werden kann. Trick: Ein Page-Token, das aus
einem **langlebigen User-Token** gezogen wird, läuft nicht ab (solange App + Rechte bestehen).

> Token **nie in den Chat** und **nie committen**. Alle Schritte laufen lokal bei dir.

## Tooling in diesem Repo
- `facebook_token.py` — holt + **prüft** das Page-Token in einem Rutsch (ersetzt die 3 curl-Schritte).
- `facebook_post.py` — postet Video/Reel (`/{page}/videos`) oder Foto (`/{page}/photos`).
- In `post_next_reel.py` als 5. Kanal verdrahtet; im Workflow `luxestyle-social.yml` als
  `FB_PAGE_ACCESS_TOKEN` (Fallback `META_ACCESS_TOKEN`).

## Offizielle Links
- Graph API Explorer (Token erzeugen): https://developers.facebook.com/tools/explorer/
- Access Token Debugger (Ablauf prüfen): https://developers.facebook.com/tools/debug/accesstoken/
- Long-Lived Tokens: https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived/
- Page-Token-Doku: https://developers.facebook.com/docs/pages/access-tokens/

## Der schnelle Weg (empfohlen)
1. **Graph API Explorer** öffnen → oben rechts App **„LuxeStyle Social"** wählen.
2. **„Generate Access Token"** → diese Scopes anhaken:
   `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, `pages_manage_engagement`,
   `instagram_basic`, `instagram_content_publish`
   (`pages_manage_engagement` = Spam-Moderation/Kommentare ausblenden.)
3. Das (kurzlebige) **USER-Token** kopieren.
4. Lokal ausführen (Token wird **nicht** als Argument übergeben → nicht in der Shell-History):
   ```
   FB_APP_ID=DEINE_APP_ID FB_APP_SECRET=DEIN_APP_SECRET python content/tools/facebook_token.py
   ```
   Das Skript fragt das USER-Token ab, tauscht es, zieht das Page-Token und prüft
   **Type=PAGE** + **Expires=Never**. Am Ende gibt es das fertige Page-Token aus.
5. Als GitHub-Secrets setzen (**Repo → Settings → Secrets and variables → Actions**):
   - `FB_PAGE_ACCESS_TOKEN` = das Page-Token
   - `META_ACCESS_TOKEN` = dasselbe Token (Fallback)
   - optional `IG_ACCESS_TOKEN` = dasselbe (wenn IG über dieselbe App läuft)

Danach postet der Workflow Facebook automatisch mit (sonst sauber übersprungen).

## Manuell (falls du curl bevorzugst)
```
# 1) kurzlebiges -> langlebiges User-Token (60 Tage)
curl -s "https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=KURZLEBIGES_USER_TOKEN"
# 2) Page-Token (läuft NICHT ab)
curl -s "https://graph.facebook.com/v21.0/me/accounts?access_token=LANGLEBIGES_USER_TOKEN"
#    -> Seite „LuxeStyle CH" (1049840534888592) suchen, deren access_token kopieren
# 3) prüfen: Token in den Debugger -> "Expires: Never", "Type: Page"
```

## Warum es „100× falsch" war — die echten Stolperfallen
- **App-Secret ≠ Access-Token.** Das Secret sind 32 Hex-Zeichen (z. B. `b3bbb…`). Ein Token ist
  lang (100+ Zeichen, meist `EAA…`). Secret als Token → Fehler `code 190 "Cannot parse access token"`.
  → `facebook_token.py` erkennt das und bricht mit Hinweis ab.
- **Kurzlebiges Token zu spät benutzt.** Es läuft in ~1–2 h ab. Erst Explorer-Token holen,
  **sofort** tauschen.
- **Scope `pages_show_list` fehlt** → `/me/accounts` ist leer. Alle 6 Scopes oben anhaken.
- **User-Token statt Page-Token.** Zum Posten braucht es das **Page**-Token aus `/me/accounts`,
  nicht dein persönliches User-Token.
- **Falsche Berechtigung.** Posten braucht **`pages_manage_posts`** — NICHT `pages_manage_metadata`.
- **Falsche/doppelte Seite.** Es gibt mehrere „luxestyle"-Seiten; die echte ist
  **LuxeStyle CH `1049840534888592`**. `facebook_token.py` listet sonst alle IDs auf.
- **Nicht Admin der Seite / App im Dev-Mode** → kein/leeres Page-Token.

## Medien-Hosting (wichtig)
Das Repo ist **privat** → GitHub-Raw-URLs funktionieren NICHT für FB/IG/Threads.
Für `facebook_post.py --url …` eine **öffentliche Shopify-CDN-URL** nutzen
(siehe `shopify-product-videos.json`, Typ `fertige-ad-9:16`). Bilder als **JPG** (kein WebP).
`--reel <name>` (GitHub-Raw) klappt nur, falls das Repo öffentlich ist.

## Posten testen
```
# Dry-Run (kein echter Post)
FB_PAGE_ACCESS_TOKEN=… python content/tools/facebook_post.py --url <CDN-mp4> --message "Test" --dry-run
# Foto
FB_PAGE_ACCESS_TOKEN=… python content/tools/facebook_post.py --photo <CDN-jpg> --message "…"
```
