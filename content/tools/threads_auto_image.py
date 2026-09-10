#!/usr/bin/env python3
"""
LuxeStyle Threads-Auto-Poster — Threads API (graph.threads.net).

Postet 1 rotierenden Beitrag (REEL/Video oder Bild) auf Threads. Medien liegen
auf der **oeffentlichen Shopify-CDN** (Repo ist privat -> GitHub-Raw geht nicht).

ENV (nie committen):
  THREADS_ACCESS_TOKEN   (Long-Lived, Scope threads_content_publish)
  THREADS_USER_ID        (optional; sonst via /me)
  POST_INDEX             (optional; erzwingt einen festen Eintrag)

Rotation: Index nach UTC (Tag*2 + AM/PM) modulo Anzahl Eintraege.
Nur Standardbibliothek (urllib).
"""
import os, json, time, sys, urllib.request, urllib.parse, urllib.error
from datetime import datetime, timezone

GT = "https://graph.threads.net"
IMG = "https://cdn.shopify.com/s/files/1/0943/6856/3585/files/"
VID = "https://cdn.shopify.com/videos/c/vp/"

# Rotierende Beitraege: fertige 9:16-Reels (Video) + saubere Produktbilder.
POSTS = [
    {"type": "VIDEO", "url": VID + "9ba0c3f017ad486a902be4fc5ff3f215/9ba0c3f017ad486a902be4fc5ff3f215.HD-1080p-2.5Mbps-85362926.mp4",
     "cap": "LuxeStyle Sommer 2026 ✨ Highlights aus der Schweiz – Mode, Schmuck & mehr \U0001F1E8\U0001F1ED "
            "-10% mit Code WELCOME10 → luxestyle.ch #luxestyle #sommer2026 #swissmade #fashion #reels"},
    {"type": "IMAGE", "url": IMG + "fa7f66fa-bf2d-4800-835e-2e3fe6984427.jpg",
     "cap": "Klassisch & elegant: das aermellose Sommerkleid. Premium aus der Schweiz. "
            "-10% mit Code WELCOME10 → luxestyle.ch #luxestyle #sommer2026 #ootd #swissmade"},
    {"type": "VIDEO", "url": VID + "5637452c09574c2e8b296f40c5155fbf/5637452c09574c2e8b296f40c5155fbf.HD-1080p-2.5Mbps-85361886.mp4",
     "cap": "Unsere Bestseller \U0001F3C6 LuxeStyle Top-10 aus der Schweiz. "
            "-10% mit Code WELCOME10 → luxestyle.ch #luxestyle #bestseller #swissmade #sommer2026"},
    {"type": "IMAGE", "url": IMG + "6a966077-7211-437d-b80c-d6025f44ba18.jpg",
     "cap": "Boho-Vibes ☀️ Kleid «Ibiza» aus Baumwoll-Leinen. "
            "-10% mit Code WELCOME10 → luxestyle.ch #luxestyle #boho #sommerlook #swissmade"},
    {"type": "VIDEO", "url": VID + "284fe922e443486da17bf1797d1867dc/284fe922e443486da17bf1797d1867dc.HD-1080p-2.5Mbps-85361887.mp4",
     "cap": "Schau dich um \U0001F6CD️ LuxeStyle – Premium-Lifestyle aus der Schweiz. "
            "-10% mit Code WELCOME10 → luxestyle.ch #luxestyle #shopping #swissmade #sommer2026"},
    {"type": "IMAGE", "url": IMG + "b4da0d58-e760-4691-b348-9dc4a3d13722.jpg",
     "cap": "Retro-Sandalen mit Komfort-Sohle \U0001F461 Dein Sommer-Begleiter. "
            "-10% mit Code WELCOME10 → luxestyle.ch #luxestyle #accessoires #sommer2026 #swissmade"},
]


def jget(u):
    try:
        return json.load(urllib.request.urlopen(u, timeout=60)), None
    except urllib.error.HTTPError as e:
        return None, e.read().decode()[:400]
    except Exception as e:
        return None, "NETERR:" + str(e)[:200]


def jpost(u, p):
    d = urllib.parse.urlencode(p).encode()
    try:
        return json.load(urllib.request.urlopen(urllib.request.Request(u, data=d), timeout=120)), None
    except urllib.error.HTTPError as e:
        return None, e.read().decode()[:400]
    except Exception as e:
        return None, "NETERR:" + str(e)[:200]


def main():
    tok = os.environ.get("THREADS_ACCESS_TOKEN")
    if not tok:
        print("uebersprungen: THREADS_ACCESS_TOKEN nicht gesetzt.")
        return 0
    uid = os.environ.get("THREADS_USER_ID")
    if not uid:
        me, err = jget(GT + "/v1.0/me?" + urllib.parse.urlencode({"fields": "id", "access_token": tok}))
        if err:
            sys.exit("me-Fehler: " + err)
        uid = me["id"]

    env_idx = os.environ.get("POST_INDEX")
    if env_idx not in (None, ""):
        idx = int(env_idx) % len(POSTS)
    else:
        now = datetime.now(timezone.utc)
        idx = (now.timetuple().tm_yday * 2 + (0 if now.hour < 14 else 1)) % len(POSTS)
    p = POSTS[idx]
    print("Threads-Auto #%d (%s)" % (idx, p["type"]))

    params = {"media_type": p["type"], "text": p["cap"], "access_token": tok}
    params["video_url" if p["type"] == "VIDEO" else "image_url"] = p["url"]
    c, err = jpost(GT + "/v1.0/%s/threads" % uid, params)
    if err:
        sys.exit("Container-Fehler: " + err)
    cid = c["id"]
    tries = 45 if p["type"] == "VIDEO" else 20
    for _ in range(tries):
        time.sleep(4)
        st, e = jget(GT + "/v1.0/%s?" % cid + urllib.parse.urlencode({"fields": "status", "access_token": tok}))
        if st and st.get("status") == "FINISHED":
            break
        if st and st.get("status") == "ERROR":
            sys.exit("Verarbeitung ERROR: " + json.dumps(st)[:300])
    pub, err = jpost(GT + "/v1.0/%s/threads_publish" % uid, {"creation_id": cid, "access_token": tok})
    if err:
        sys.exit("Publish-Fehler: " + err)
    print("VEROEFFENTLICHT post_id", pub.get("id"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
