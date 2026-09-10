#!/usr/bin/env python3
"""
LuxeStyle Facebook-Seiten-Post  —  Facebook **Graph API** (Seite „LuxeStyle CH").

Postet ein Video/Reel oder ein Foto auf die Facebook-Seite. Braucht ein **Page-Token**
mit `pages_manage_posts` (NICHT `pages_manage_metadata`!). Page-Token am besten langlebig/
nie ablaufend holen mit `facebook_token.py` (siehe FB_TOKEN_SETUP.md).

Endpunkte:
  Video:  POST /{page-id}/videos   (file_url = öffentliche MP4-URL, description = Text)
  Foto:   POST /{page-id}/photos   (url = öffentliche Bild-URL, caption = Text)

⚠️ MEDIEN-HOSTING: Das Repo ist **privat** → GitHub-Raw-URLs funktionieren NICHT.
   Für `--url` eine **öffentliche Shopify-CDN-URL** nutzen (siehe shopify-product-videos.json).
   `--reel <name>` baut zwar die GitHub-Raw-URL, klappt aber nur, wenn das Repo öffentlich ist.

ENV (nie committen):
  FB_PAGE_ACCESS_TOKEN   (Page-Token; Fallback: META_ACCESS_TOKEN)
  FB_PAGE_ID             (optional, Default = LuxeStyle CH 1049840534888592)

Nutzung:
  python facebook_post.py --url <öffentliche-mp4-url> --message "… 10% mit WELCOME10 #luxestyle"
  python facebook_post.py --photo <öffentliche-jpg-url> --message "…"
  python facebook_post.py --reel LuxeStyle_Sommer_AdSafe.mp4 --message "…"   # nur bei öffentl. Repo
  python facebook_post.py --url … --dry-run

Nur Standardbibliothek (urllib).
"""
import os, sys, json, argparse, urllib.parse, urllib.request, urllib.error

GRAPH = "https://graph.facebook.com/v21.0"
RAW = "https://raw.githubusercontent.com/allengchour-glitch/luxestyle-dashboard/main/content/ads/"
DEFAULT_PAGE = "1049840534888592"   # LuxeStyle CH


def creds():
    tok = os.environ.get("FB_PAGE_ACCESS_TOKEN") or os.environ.get("META_ACCESS_TOKEN")
    if not tok:
        sys.exit("Bitte ENV setzen: FB_PAGE_ACCESS_TOKEN (oder META_ACCESS_TOKEN).\n"
                 "Page-Token holen: python facebook_token.py  (siehe FB_TOKEN_SETUP.md).")
    page = os.environ.get("FB_PAGE_ID", DEFAULT_PAGE)
    return page, tok


def _post(path, params):
    data = urllib.parse.urlencode(params).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(GRAPH + path, data=data), timeout=180) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:700]
        hint = ""
        if "pages_manage_posts" in body or "(#200)" in body or "permission" in body.lower():
            hint = ("\nHINWEIS: Das Token braucht **pages_manage_posts** und muss ein **Page**-Token "
                    "der Seite sein (nicht dein User-Token). Mit facebook_token.py neu holen.")
        if "Error validating access token" in body or "code\":190" in body or "code\": 190" in body:
            hint = ("\nHINWEIS: Token ungültig/abgelaufen — oder du hast aus Versehen das **App-Secret** "
                    "(32 Hex) statt eines Access-Tokens gesetzt. Echtes Token ist lang (100+ Zeichen).")
        sys.exit("FB HTTP %s: %s%s" % (e.code, body, hint))


def main():
    ap = argparse.ArgumentParser(description="Facebook-Seite: Video/Reel oder Foto posten (Graph API)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--url", help="öffentliche MP4-URL (Video/Reel)")
    g.add_argument("--reel", help="Reel-Dateiname in content/ads/ -> GitHub-Raw-URL (nur bei öffentl. Repo)")
    g.add_argument("--photo", help="öffentliche Bild-URL (JPG/PNG)")
    ap.add_argument("--message", default="Entdecke LuxeStyle – Premium aus der Schweiz. 10% mit Code WELCOME10 #luxestyle #swissmade",
                    help="Begleittext / Caption")
    ap.add_argument("--page", help="Page-ID überschreiben (Default = LuxeStyle CH)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    is_photo = bool(a.photo)
    media_url = a.photo or a.url or (RAW + a.reel)
    kind = "Foto" if is_photo else "Video/Reel"
    print("→ Facebook-%s: %s" % (kind, media_url))
    print("  Text:", a.message)
    if a.dry_run:
        ep = "/photos (url)" if is_photo else "/videos (file_url)"
        print("DRY-RUN — würde POST auf /{page}%s machen." % ep)
        return

    page, tok = creds()
    if a.page:
        page = a.page

    if is_photo:
        res = _post("/%s/photos" % page, {"url": media_url, "caption": a.message, "access_token": tok})
    else:
        res = _post("/%s/videos" % page, {"file_url": media_url, "description": a.message, "access_token": tok})

    post_id = res.get("post_id") or res.get("id")
    if post_id:
        print("✅ Facebook gepostet · id:", post_id)
    else:
        sys.exit("Antwort: " + json.dumps(res)[:400])


if __name__ == "__main__":
    main()
