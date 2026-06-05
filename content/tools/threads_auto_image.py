#!/usr/bin/env python3
"""
LuxeStyle Threads-Auto-Poster (BILDER) — Threads API (graph.threads.net).

Postet 1 rotierendes, ad-safe Produktbild (oeffentliche Shopify-CDN-URL) als
Threads-Post. Bilder statt Video, weil das Repo privat ist (Threads kann
private GitHub-Raw-Videos nicht laden) — Shopify-CDN-Bilder sind oeffentlich.

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
CDN = "https://cdn.shopify.com/s/files/1/0943/6856/3585/files/"

# (Bilddatei auf Shopify-CDN, Caption) — saubere, ad-safe Produktbilder
POSTS = [
    ("fa7f66fa-bf2d-4800-835e-2e3fe6984427.jpg",
     "Klassisch & elegant: das aermellose Sommerkleid ✨ Premium aus der Schweiz. "
     "-10% mit Code WELCOME10 → luxestyle.ch #luxestyle #sommer2026 #swissmade #ootd"),
    ("c6efdee1-e741-4788-b96b-b5a96095e3d9.jpg",
     "Verspielt in den Sommer \U0001F338 Mini-Kleid mit Rueschen. "
     "-10% mit Code WELCOME10 → luxestyle.ch #luxestyle #sommerlook #fashion #swissmade"),
    ("dc7ee2ce-fcc5-4f61-8622-ab04356f6cd7.jpg",
     "Beach-ready \U0001F334 Maxikleid «Bali», luftig & leicht. "
     "-10% mit Code WELCOME10 → luxestyle.ch #luxestyle #strandlook #sommer2026 #boho"),
    ("6a966077-7211-437d-b80c-d6025f44ba18.jpg",
     "Boho-Vibes ☀️ Kleid «Ibiza» aus Baumwoll-Leinen. "
     "-10% mit Code WELCOME10 → luxestyle.ch #luxestyle #boho #sommerlook #swissmade"),
    ("3136e619-9947-4d5f-8248-707c65d055d2.jpg",
     "Leicht & schulterfrei: «Brise» fuer laue Sommerabende. "
     "-10% mit Code WELCOME10 → luxestyle.ch #luxestyle #ootd #sommer2026 #fashion"),
    ("b4da0d58-e760-4691-b348-9dc4a3d13722.jpg",
     "Retro-Sandalen mit Komfort-Sohle \U0001F461 Dein Sommer-Begleiter. "
     "-10% mit Code WELCOME10 → luxestyle.ch #luxestyle #accessoires #sommer2026 #swissmade"),
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
    fname, caption = POSTS[idx]
    image_url = CDN + fname
    print("Threads-Bildpost #%d: %s" % (idx, fname))

    c, err = jpost(GT + "/v1.0/%s/threads" % uid,
                   {"media_type": "IMAGE", "image_url": image_url, "text": caption, "access_token": tok})
    if err:
        sys.exit("Container-Fehler: " + err)
    cid = c["id"]
    for _ in range(20):
        time.sleep(3)
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
