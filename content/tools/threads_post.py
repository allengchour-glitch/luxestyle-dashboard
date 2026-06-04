#!/usr/bin/env python3
"""
LuxeStyle Threads-Post  —  Meta **Threads API** (graph.threads.net).

Threads ist eine **eigene** API (nicht IG-Graph): Container anlegen -> Status pollen
-> threads_publish. Scopes der Threads-App: threads_basic + threads_content_publish.

Video muss unter einer **öffentlichen URL** liegen (9:16 ok). Wir nutzen die
**GitHub-Raw-URL** des committeten Reels (gratis Hosting):
  https://raw.githubusercontent.com/allengchour-glitch/luxestyle-dashboard/main/content/ads/<reel>.mp4

ENV (nie committen):
  THREADS_ACCESS_TOKEN   (Long-Lived-Token, Scope threads_content_publish)
  THREADS_USER_ID        (optional; sonst via /me automatisch geholt)

Nutzung:
  python threads_post.py --url <öffentliche-mp4-url> --caption "… -10% mit WELCOME10"
  python threads_post.py --reel LuxeStyle_Sommer_AdSafe.mp4 --caption "…"   # baut Raw-URL selbst
  python threads_post.py --reel … --text-only --caption "…"                 # reiner Textpost
  python threads_post.py --url … --dry-run

Nur Standardbibliothek (urllib).
"""
import os, sys, json, time, argparse, urllib.parse, urllib.request, urllib.error

GRAPH = "https://graph.threads.net/v1.0"
RAW = "https://raw.githubusercontent.com/allengchour-glitch/luxestyle-dashboard/main/content/ads/"


def _token():
    tok = os.environ.get("THREADS_ACCESS_TOKEN")
    if not tok:
        sys.exit("Bitte ENV setzen: THREADS_ACCESS_TOKEN (Threads-App, Scope threads_content_publish).")
    return tok


def _post(path, params):
    data = urllib.parse.urlencode(params).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(GRAPH + path, data=data), timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit("Threads HTTP %s: %s" % (e.code, e.read().decode()[:600]))


def _get(path, params):
    url = GRAPH + path + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit("Threads HTTP %s: %s" % (e.code, e.read().decode()[:600]))


def _user_id(tok):
    uid = os.environ.get("THREADS_USER_ID")
    if uid:
        return uid
    me = _get("/me", {"fields": "id,username", "access_token": tok})
    uid = me.get("id")
    if not uid:
        sys.exit("Keine THREADS_USER_ID und /me ohne id: " + json.dumps(me)[:300])
    print("  THREADS_USER_ID (via /me):", uid, "(@%s)" % me.get("username", "?"))
    return uid


def main():
    ap = argparse.ArgumentParser(description="Threads: Reel/Post veröffentlichen (Threads API)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--url", help="öffentliche MP4-URL")
    g.add_argument("--reel", help="Reel-Dateiname in content/ads/ -> baut GitHub-Raw-URL")
    ap.add_argument("--caption", default="Entdecke LuxeStyle – Premium aus der Schweiz 🇨🇭 -10% mit Code WELCOME10")
    ap.add_argument("--text-only", action="store_true", help="reiner Textpost (kein Video)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    video_url = a.url or (RAW + a.reel)
    text = a.caption[:500]  # Threads-Textlimit
    if a.text_only:
        print("→ Threads-Textpost")
    else:
        print("→ Threads-Video:", video_url)
    print("  Text:", text)
    if a.dry_run:
        print("DRY-RUN — würde Container anlegen (media_type=%s) → pollen → threads_publish." %
              ("TEXT" if a.text_only else "VIDEO"))
        return

    tok = _token()
    uid = _user_id(tok)

    print("→ Container anlegen …")
    params = {"text": text, "access_token": tok}
    if a.text_only:
        params["media_type"] = "TEXT"
    else:
        params["media_type"] = "VIDEO"
        params["video_url"] = video_url
    cont = _post("/%s/threads" % uid, params)
    cid = cont.get("id")
    if not cid:
        sys.exit("Kein Container: " + json.dumps(cont)[:400])
    print("  container:", cid, "· warte auf Verarbeitung …")

    # Video braucht Verarbeitungszeit; Text ist sofort fertig.
    if not a.text_only:
        for _ in range(30):
            time.sleep(4)
            st = _get("/%s" % cid, {"fields": "status,error_message", "access_token": tok})
            sc = st.get("status")
            if sc == "FINISHED":
                break
            if sc == "ERROR":
                sys.exit("  ✗ Verarbeitung fehlgeschlagen: " + json.dumps(st)[:400])
        else:
            sys.exit("  ✗ Timeout bei Container-Verarbeitung.")

    print("→ Veröffentlichen …")
    pub = _post("/%s/threads_publish" % uid, {"creation_id": cid, "access_token": tok})
    if pub.get("id"):
        print("✅ Threads-Post veröffentlicht · id:", pub["id"])
    else:
        sys.exit("Publish-Antwort: " + json.dumps(pub)[:400])


if __name__ == "__main__":
    main()
