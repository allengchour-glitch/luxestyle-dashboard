#!/usr/bin/env python3
"""
Multi-Kanal-Poster: postet je Lauf 1 rotierendes ad-safe Reel auf alle Kanäle, deren
Token gesetzt sind — sonst sauber übersprungen.

  • Telegram  (TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID)      -> social_post.py  (Video, LOKALE Datei)
  • TikTok    (TIKTOK_OPEN_ACCESS_TOKEN)                   -> tiktok_post.py  (Entwurf, LOKALE Datei)
  • Instagram (IG_USER_ID + IG_ACCESS_TOKEN)               -> instagram_post.py (Reel, CDN-URL)
  • Threads   (THREADS_ACCESS_TOKEN [+ THREADS_USER_ID])   -> threads_post.py  (Video, CDN-URL)
  • Facebook  (FB_PAGE_ACCESS_TOKEN | META_ACCESS_TOKEN)   -> facebook_post.py (Seite, CDN-URL)

WICHTIG: Das Repo ist **privat** → GitHub-Raw-URLs sind NICHT öffentlich, FB/IG/Threads können
das Video dann nicht laden. Darum nutzen diese drei Kanäle die **öffentlichen Shopify-CDN-URLs**
aus `captions.json` → `cdn_reels`. Telegram/TikTok laden die lokale Datei direkt hoch.

Rotation: Index = UTC-Stunde (bzw. ENV REEL_INDEX), je Quelle modulo ihrer Länge.
Für die GitHub-Action (luxestyle-social.yml).
"""
import os, json, subprocess, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ADS = os.path.normpath(os.path.join(HERE, "..", "ads"))
DOMAIN = "https://luxestyle.ch"

with open(os.path.join(HERE, "captions.json"), encoding="utf-8") as f:
    DATA = json.load(f)
REELS = DATA["reels"]
CDN = DATA.get("cdn_reels", [])

env_idx = os.environ.get("REEL_INDEX")
hour = int(env_idx) if env_idx not in (None, "") else datetime.now(timezone.utc).hour

local = REELS[hour % len(REELS)]
fname, caption = local["file"], local["caption"]
path = os.path.join(ADS, fname)
have_local = os.path.exists(path)

cdn = CDN[hour % len(CDN)] if CDN else None  # {cdn_url, theme, caption}

print("→ Lokal #%d: %s (%s)" % (hour % len(REELS), fname, local.get("theme", "")))
if cdn:
    print("→ CDN  #%d: %s" % (hour % len(CDN), cdn.get("theme", "")))
py = sys.executable
done, skipped = [], []


def run(args):
    return subprocess.call([py] + args)


# 1) Telegram (Video, lokale Datei)
if os.environ.get("TELEGRAM_BOT_TOKEN") and os.environ.get("TELEGRAM_CHAT_ID"):
    if have_local:
        rc = run([os.path.join(HERE, "social_post.py"), "--video", path, "--text", caption, "--link", DOMAIN])
        (done if rc == 0 else skipped).append("telegram")
    else:
        skipped.append("telegram(reel fehlt)")
else:
    skipped.append("telegram(kein Token)")

# 2) TikTok (Entwurf, lokale Datei)
if os.environ.get("TIKTOK_OPEN_ACCESS_TOKEN"):
    if have_local:
        rc = run([os.path.join(HERE, "tiktok_post.py"), path])
        (done if rc == 0 else skipped).append("tiktok-draft")
    else:
        skipped.append("tiktok(reel fehlt)")
else:
    skipped.append("tiktok(kein Token)")

# 3) Instagram (Reel via CDN-URL)
if os.environ.get("IG_USER_ID") and os.environ.get("IG_ACCESS_TOKEN"):
    if cdn:
        rc = run([os.path.join(HERE, "instagram_post.py"), "--url", cdn["cdn_url"], "--caption", cdn["caption"]])
        (done if rc == 0 else skipped).append("instagram")
    else:
        skipped.append("instagram(keine CDN-URL)")
else:
    skipped.append("instagram(kein Token)")

# 4) Threads (Video via CDN-URL)
if os.environ.get("THREADS_ACCESS_TOKEN"):
    if cdn:
        rc = run([os.path.join(HERE, "threads_post.py"), "--url", cdn["cdn_url"], "--caption", cdn["caption"]])
        (done if rc == 0 else skipped).append("threads")
    else:
        skipped.append("threads(keine CDN-URL)")
else:
    skipped.append("threads(kein Token)")

# 5) Facebook-Seite (Video via CDN-URL)
if os.environ.get("FB_PAGE_ACCESS_TOKEN") or os.environ.get("META_ACCESS_TOKEN"):
    if cdn:
        rc = run([os.path.join(HERE, "facebook_post.py"), "--url", cdn["cdn_url"], "--message", cdn["caption"]])
        (done if rc == 0 else skipped).append("facebook")
    else:
        skipped.append("facebook(keine CDN-URL)")
else:
    skipped.append("facebook(kein Token)")

print("✓ gepostet:", ", ".join(done) or "—", "| übersprungen:", ", ".join(skipped) or "—")
