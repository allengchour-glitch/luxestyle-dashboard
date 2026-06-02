#!/usr/bin/env python3
"""
LuxeStyle TikTok-Ad-Upload  —  lädt ein fertiges Reel/Video in den TikTok Ads
Manager (Creative Library des Werbekontos) per **TikTok Marketing API**.

Paart sich mit build_reel.py:  build_reel.py -> fertiges MP4 -> tiktok_upload.py -> Ad-Konto.

Was es kann:
  • Video hochladen – per lokaler Datei (UPLOAD_BY_FILE, mit MD5-Signatur) ODER per URL
  • optional ein Cover-Bild hochladen
  • gibt video_id + Vorschau zurück (danach im Ads Manager als Ad-Creative nutzbar)
  • Videos im Konto auflisten (--list)

Voraussetzungen (ENV – nichts committen!):
  TIKTOK_ACCESS_TOKEN   = Access-Token einer genehmigten TikTok-for-Business-App
  TIKTOK_ADVERTISER_ID  = Werbekonto-ID (Ads Manager -> Konto-Info)
Token/Advertiser-ID gibt's im TikTok-Developer-/Business-Portal (Browser, einmalig).

Nutzung:
  python tiktok_upload.py reel.mp4 --name "LuxeStyle Sommer A"
  python tiktok_upload.py --url https://cdn.../reel.mp4 --name "Sommer B"
  python tiktok_upload.py reel.mp4 --cover cover.jpg
  python tiktok_upload.py --list

Nur Standardbibliothek (urllib). Kein pip nötig.
Hinweis: Das eigentliche *Schalten* der Ad (Kampagne/AdGroup/Ad) macht man danach im
Ads Manager oder über die Campaign-Endpoints – dieses Tool legt das Creative bereit.
"""
import os, sys, json, hashlib, mimetypes, argparse, urllib.request, urllib.error

BASE = "https://business-api.tiktok.com/open_api/v1.3"

def creds():
    tok = os.environ.get("TIKTOK_ACCESS_TOKEN")
    adv = os.environ.get("TIKTOK_ADVERTISER_ID")
    if not (tok and adv):
        sys.exit("Bitte ENV setzen:\n  TIKTOK_ACCESS_TOKEN=...\n  TIKTOK_ADVERTISER_ID=...\n"
                 "(Token + Advertiser-ID aus dem TikTok-for-Business-/Developer-Portal.)")
    return tok, adv

def _api(method, path, token, json_body=None, multipart=None):
    url = BASE + path
    headers = {"Access-Token": token}
    data = None
    if json_body is not None:
        data = json.dumps(json_body).encode(); headers["Content-Type"] = "application/json"
    elif multipart is not None:
        boundary = "----luxe" + hashlib.md5(os.urandom(8)).hexdigest()
        body = bytearray()
        for k, v in multipart["fields"].items():
            body += b"--%s\r\n" % boundary.encode()
            body += b'Content-Disposition: form-data; name="%s"\r\n\r\n%s\r\n' % (k.encode(), str(v).encode())
        for k, (fname, content, ctype) in multipart["files"].items():
            body += b"--%s\r\n" % boundary.encode()
            body += b'Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (k.encode(), fname.encode())
            body += b"Content-Type: %s\r\n\r\n" % ctype.encode()
            body += content + b"\r\n"
        body += b"--%s--\r\n" % boundary.encode()
        data = bytes(body); headers["Content-Type"] = "multipart/form-data; boundary=" + boundary
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            out = json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit("HTTP %s: %s" % (e.code, e.read().decode()[:800]))
    if out.get("code") not in (0, None):
        sys.exit("TikTok-API-Fehler %s: %s" % (out.get("code"), out.get("message")))
    return out

def upload_by_url(token, adv, url, name):
    body = {"advertiser_id": adv, "upload_type": "UPLOAD_BY_URL", "video_url": url}
    if name: body["file_name"] = name
    return _api("POST", "/file/video/ad/upload/", token, json_body=body)

def upload_by_file(token, adv, path, name):
    with open(path, "rb") as f: content = f.read()
    sig = hashlib.md5(content).hexdigest()
    ctype = mimetypes.guess_type(path)[0] or "video/mp4"
    fields = {"advertiser_id": adv, "upload_type": "UPLOAD_BY_FILE", "video_signature": sig,
              "file_name": name or os.path.basename(path)}
    files = {"video_file": (os.path.basename(path), content, ctype)}
    return _api("POST", "/file/video/ad/upload/", token, multipart={"fields": fields, "files": files})

def upload_cover(token, adv, path):
    with open(path, "rb") as f: content = f.read()
    sig = hashlib.md5(content).hexdigest()
    ctype = mimetypes.guess_type(path)[0] or "image/jpeg"
    fields = {"advertiser_id": adv, "upload_type": "UPLOAD_BY_FILE", "image_signature": sig,
              "file_name": os.path.basename(path)}
    files = {"image_file": (os.path.basename(path), content, ctype)}
    return _api("POST", "/file/image/ad/upload/", token, multipart={"fields": fields, "files": files})

def list_videos(token, adv, n=20):
    import urllib.parse
    q = urllib.parse.urlencode({"advertiser_id": adv, "page_size": n})
    return _api("GET", "/file/video/ad/search/?" + q, token)

def main():
    ap = argparse.ArgumentParser(description="TikTok-Ad-Upload (Creative Library)")
    ap.add_argument("video", nargs="?", help="lokale MP4 (UPLOAD_BY_FILE)")
    ap.add_argument("--url", help="öffentliche Video-URL (UPLOAD_BY_URL) statt lokaler Datei")
    ap.add_argument("--name", help="Anzeigename im Ads Manager")
    ap.add_argument("--cover", help="optionales Cover-Bild (jpg/png)")
    ap.add_argument("--list", action="store_true", help="vorhandene Videos im Konto auflisten")
    a = ap.parse_args()
    token, adv = creds()

    if a.list:
        res = list_videos(token, adv)
        for v in res.get("data", {}).get("list", []):
            print("  %s  %s  %sx%s  %.1fs" % (v.get("video_id"), v.get("file_name", ""),
                  v.get("width"), v.get("height"), float(v.get("duration", 0))))
        return

    if not (a.video or a.url):
        sys.exit("Bitte eine MP4-Datei ODER --url angeben (oder --list).")

    if a.url:
        res = upload_by_url(token, adv, a.url, a.name)
    else:
        if not os.path.exists(a.video): sys.exit("Datei fehlt: " + a.video)
        res = upload_by_file(token, adv, a.video, a.name)

    data = res.get("data", {})
    item = (data.get("list") or [data])[0] if isinstance(data, dict) else {}
    vid = item.get("video_id") or data.get("video_id")
    print("✅ Video hochgeladen.")
    print("   video_id:", vid)
    if item.get("preview_url") or item.get("video_cover_url"):
        print("   preview :", item.get("preview_url") or item.get("video_cover_url"))
    if a.cover:
        c = upload_cover(token, adv, a.cover)
        cid = (c.get("data") or {}).get("image_id")
        print("   cover image_id:", cid)
    print("\nNächster Schritt: im TikTok Ads Manager das Video als Creative auswählen")
    print("(oder via Campaign-/AdGroup-/Ad-Endpoints eine Ad erstellen). Pixel: D8EQE4JC77UAEKHUJCM0,")
    print("Optimierungsereignis: Complete Payment.")

if __name__ == "__main__":
    main()
