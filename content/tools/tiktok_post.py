#!/usr/bin/env python3
"""
LuxeStyle TikTok-Profil-Post (ORGANISCH)  —  TikTok **Content Posting API**
(open.tiktokapis.com), nicht die Business/Ads-API.

Zwei Modi:
  --draft  (Default, KEIN App-Audit nötig): lädt das Reel in die TikTok-**Entwürfe/Inbox**
           des verbundenen Kontos -> du öffnest die TikTok-App und tippst 1× „Posten"
           (Caption/Cover dort, öffentlich). Scope: video.upload
  --direct (erst NACH App-Audit möglich): postet sofort öffentlich. Scope: video.publish

Upload als FILE_UPLOAD (lokale Datei, chunked) — kein Domain-Verify nötig.
(PULL_FROM_URL ginge auch, braucht aber eine im TikTok-Portal verifizierte Domain.)

ENV (nie committen / nicht im Chat):
  TIKTOK_OPEN_ACCESS_TOKEN   (Login-Kit-Token mit Scope video.upload bzw. video.publish)
                              -> via get_open_token.py holen

Nutzung:
  python tiktok_post.py ../ads/LuxeStyle_Sommer_AdSafe.mp4                 # Entwurf
  python tiktok_post.py ../ads/LuxeStyle_Sommer_AdSafe.mp4 --direct \
      --title "Sommer 2026 bei LuxeStyle ... 10% mit WELCOME10 #luxestyle"
  python tiktok_post.py ../ads/x.mp4 --dry-run

Nur Standardbibliothek (urllib).
"""
import os, sys, json, time, argparse, urllib.request, urllib.error

BASE = "https://open.tiktokapis.com/v2"
CHUNK_MAX = 64 * 1024 * 1024   # 64 MB: TikTok erlaubt das ganze Video als 1 Chunk bis 64 MB


def token():
    t = os.environ.get("TIKTOK_OPEN_ACCESS_TOKEN")
    if not t:
        sys.exit("Bitte TIKTOK_OPEN_ACCESS_TOKEN setzen (Login-Kit-Token, Scope video.upload).\n"
                 "Holen via: python get_open_token.py tiktok")
    return t


def _api(path, tok, body):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + tok,
                                          "Content-Type": "application/json; charset=UTF-8"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            out = json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit("TikTok HTTP %s: %s" % (e.code, e.read().decode()[:600]))
    err = (out.get("error") or {})
    if err.get("code") not in (None, "ok", ""):
        sys.exit("TikTok-Fehler: %s — %s" % (err.get("code"), err.get("message")))
    return out


def put_chunk(upload_url, data, start, end, total):
    req = urllib.request.Request(upload_url, data=data, method="PUT",
                                 headers={"Content-Type": "video/mp4",
                                          "Content-Length": str(len(data)),
                                          "Content-Range": "bytes %d-%d/%d" % (start, end, total)})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.status
    except urllib.error.HTTPError as e:
        sys.exit("Upload-Chunk HTTP %s: %s" % (e.code, e.read().decode()[:400]))


def main():
    ap = argparse.ArgumentParser(description="TikTok-Profil: Reel als Entwurf/Direktpost (Content Posting API)")
    ap.add_argument("video", help="lokale MP4")
    ap.add_argument("--direct", action="store_true", help="sofort öffentlich posten (braucht App-Audit + Scope video.publish)")
    ap.add_argument("--title", default="", help="Caption (nur --direct; im Entwurf gibst du sie in der App ein)")
    ap.add_argument("--privacy", default="PUBLIC_TO_EVERYONE", help="nur --direct: PUBLIC_TO_EVERYONE | SELF_ONLY | MUTUAL_FOLLOW_FRIENDS")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not os.path.exists(a.video):
        sys.exit("Datei fehlt: " + a.video)
    size = os.path.getsize(a.video)
    mode = "DIRECT (öffentlich)" if a.direct else "DRAFT (Entwurf -> in der App 1x posten)"
    print("→ TikTok %s: %s (%d KB)" % (mode, os.path.basename(a.video), size // 1024))
    if a.dry_run:
        endpoint = "/post/publish/video/init/" if a.direct else "/post/publish/inbox/video/init/"
        print("DRY-RUN — würde POST %s (FILE_UPLOAD, 1 Chunk) + Status-Polling." % endpoint)
        if a.direct: print("  post_info: title=%r privacy=%s" % (a.title, a.privacy))
        return

    if size > CHUNK_MAX:
        sys.exit("Video > 64 MB — Chunking-Erweiterung nötig (unsere Reels sind < 11 MB).")
    tok = token()
    source = {"source": "FILE_UPLOAD", "video_size": size, "chunk_size": size, "total_chunk_count": 1}
    if a.direct:
        body = {"post_info": {"title": a.title, "privacy_level": a.privacy,
                              "disable_comment": False, "disable_duet": False, "disable_stitch": False},
                "source_info": source}
        init = _api("/post/publish/video/init/", tok, body)
    else:
        init = _api("/post/publish/inbox/video/init/", tok, {"source_info": source})
    data = init.get("data", {})
    publish_id = data.get("publish_id"); upload_url = data.get("upload_url")
    if not (publish_id and upload_url):
        sys.exit("Init ohne publish_id/upload_url: " + json.dumps(init)[:400])
    print("  init ok · publish_id:", publish_id)

    with open(a.video, "rb") as f:
        content = f.read()
    put_chunk(upload_url, content, 0, size - 1, size)
    print("  upload ok · warte auf Verarbeitung …")

    for _ in range(20):
        time.sleep(3)
        st = _api("/post/publish/status/fetch/", tok, {"publish_id": publish_id}).get("data", {})
        s = st.get("status")
        if s in ("SEND_TO_USER_INBOX", "PUBLISH_COMPLETE"):
            print("  ✓ Status:", s)
            if a.direct:
                print("✅ Veröffentlicht (öffentlich) auf deinem TikTok-Profil.")
            else:
                print("✅ Im TikTok-Konto als **Entwurf/Inbox** — öffne die TikTok-App, "
                      "Benachrichtigung antippen → Caption/Cover → **Posten** (öffentlich).")
            return
        if s in ("FAILED",):
            sys.exit("  ✗ Fehlgeschlagen: " + json.dumps(st)[:400])
    print("  (noch in Verarbeitung — in der TikTok-App prüfen.)")


if __name__ == "__main__":
    main()
