#!/usr/bin/env python3
"""
LuxeStyle Instagram-Reel-Post  —  Instagram **Graph Content-Publishing-API**.

Voraussetzung: IG-**Business**-Konto, mit einer **Facebook-Seite** verknüpft, + Meta-App-Token.
Flow: Container anlegen (media_type=REELS, video_url) -> Status pollen -> media_publish.

Video muss unter einer **öffentlichen URL** liegen (9:16, 5–90s). Wir nutzen die
**GitHub-Raw-URL** des committeten Reels (gratis Hosting):
  https://raw.githubusercontent.com/allengchour-glitch/luxestyle-dashboard/main/content/ads/<reel>.mp4

ENV (nie committen):
  IG_USER_ID        (Instagram-Business-Account-ID; via get_open_token.py meta)
  IG_ACCESS_TOKEN   (Long-Lived-Token mit instagram_business_content_publish)

Nutzung:
  python instagram_post.py --url <öffentliche-mp4-url> --caption "… 10% mit WELCOME10 #luxestyle"
  python instagram_post.py --reel LuxeStyle_Sommer_AdSafe.mp4 --caption "…"   # baut Raw-URL selbst
  python instagram_post.py --url … --dry-run

Nur Standardbibliothek (urllib).
"""
import os, sys, json, time, argparse, urllib.parse, urllib.request, urllib.error

GRAPH = "https://graph.facebook.com/v21.0"
RAW = "https://raw.githubusercontent.com/allengchour-glitch/luxestyle-dashboard/main/content/ads/"


def creds():
    uid = os.environ.get("IG_USER_ID"); tok = os.environ.get("IG_ACCESS_TOKEN")
    if not (uid and tok):
        sys.exit("Bitte ENV setzen: IG_USER_ID + IG_ACCESS_TOKEN\n"
                 "(IG-Business-Konto + FB-Seite + Meta-App; via get_open_token.py meta).")
    return uid, tok


def _post(path, params):
    data = urllib.parse.urlencode(params).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(GRAPH + path, data=data), timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit("IG HTTP %s: %s" % (e.code, e.read().decode()[:600]))


def _get(path, params):
    url = GRAPH + path + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit("IG HTTP %s: %s" % (e.code, e.read().decode()[:600]))


def main():
    ap = argparse.ArgumentParser(description="Instagram: Reel veröffentlichen (Graph API)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--url", help="öffentliche MP4-URL")
    g.add_argument("--reel", help="Reel-Dateiname in content/ads/ -> baut GitHub-Raw-URL")
    ap.add_argument("--caption", default="Entdecke LuxeStyle – Premium aus der Schweiz 🇨🇭 10% mit Code WELCOME10 #luxestyle #swissmade")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    video_url = a.url or (RAW + a.reel)
    print("→ Instagram-Reel:", video_url)
    print("  Caption:", a.caption)
    if a.dry_run:
        print("DRY-RUN — würde Container (media_type=REELS) anlegen → pollen → media_publish.")
        return

    uid, tok = creds()
    print("→ Container anlegen …")
    cont = _post("/%s/media" % uid, {"media_type": "REELS", "video_url": video_url,
                                     "caption": a.caption, "access_token": tok})
    cid = cont.get("id")
    if not cid:
        sys.exit("Kein Container: " + json.dumps(cont)[:400])
    print("  container:", cid, "· warte auf Verarbeitung …")

    for _ in range(30):
        time.sleep(4)
        st = _get("/%s" % cid, {"fields": "status_code,status", "access_token": tok})
        sc = st.get("status_code")
        if sc == "FINISHED":
            break
        if sc == "ERROR":
            sys.exit("  ✗ Verarbeitung fehlgeschlagen: " + json.dumps(st)[:400])
    else:
        sys.exit("  ✗ Timeout bei Container-Verarbeitung.")

    print("→ Veröffentlichen …")
    pub = _post("/%s/media_publish" % uid, {"creation_id": cid, "access_token": tok})
    if pub.get("id"):
        print("✅ Instagram-Reel veröffentlicht · media_id:", pub["id"])
    else:
        sys.exit("Publish-Antwort: " + json.dumps(pub)[:400])


if __name__ == "__main__":
    main()
