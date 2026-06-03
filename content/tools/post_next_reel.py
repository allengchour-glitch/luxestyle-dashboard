#!/usr/bin/env python3
"""
Multi-Kanal-Poster: postet **1 rotierendes ad-safe Reel** (Index = Stunde) auf alle
Kanäle, deren Token gesetzt sind — sonst sauber übersprungen.

  • Telegram  (TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID)      -> social_post.py  (Video)
  • TikTok    (TIKTOK_OPEN_ACCESS_TOKEN)                   -> tiktok_post.py  (Entwurf, 1x App-Tipp)
  • Instagram (IG_USER_ID + IG_ACCESS_TOKEN)               -> instagram_post.py (Reel, GitHub-Raw-URL)

Reels + Captions kommen aus captions.json (Rotation = Reihenfolge dort).
Für die GitHub-Action (luxestyle-social.yml / luxestyle-reels-hourly.yml).
ENV REEL_INDEX erzwingt einen festen Index (sonst UTC-Stunde mod N).
"""
import os, json, subprocess, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ADS = os.path.normpath(os.path.join(HERE, "..", "ads"))
DOMAIN = "https://luxestyle.ch"

with open(os.path.join(HERE, "captions.json"), encoding="utf-8") as f:
    REELS = json.load(f)["reels"]

env_idx = os.environ.get("REEL_INDEX")
idx = (int(env_idx) if env_idx not in (None, "") else datetime.now(timezone.utc).hour) % len(REELS)
r = REELS[idx]
fname, theme, caption = r["file"], r["theme"], r["caption"]
path = os.path.join(ADS, fname)
if not os.path.exists(path):
    sys.exit("Reel fehlt: " + path)

print("→ Reel #%d: %s (%s)" % (idx, fname, theme))
py = sys.executable
done, skipped = [], []

# 1) Telegram (Video)
if os.environ.get("TELEGRAM_BOT_TOKEN") and os.environ.get("TELEGRAM_CHAT_ID"):
    rc = subprocess.call([py, os.path.join(HERE, "social_post.py"),
                          "--video", path, "--text", caption, "--link", DOMAIN])
    (done if rc == 0 else skipped).append("telegram")
else:
    skipped.append("telegram(kein Token)")

# 2) TikTok (Entwurf -> in der App 1x posten)
if os.environ.get("TIKTOK_OPEN_ACCESS_TOKEN"):
    rc = subprocess.call([py, os.path.join(HERE, "tiktok_post.py"), path])
    (done if rc == 0 else skipped).append("tiktok-draft")
else:
    skipped.append("tiktok(kein Token)")

# 3) Instagram (Reel via GitHub-Raw-URL)
if os.environ.get("IG_USER_ID") and os.environ.get("IG_ACCESS_TOKEN"):
    rc = subprocess.call([py, os.path.join(HERE, "instagram_post.py"),
                          "--reel", fname, "--caption", caption])
    (done if rc == 0 else skipped).append("instagram")
else:
    skipped.append("instagram(kein Token)")

print("✓ gepostet:", ", ".join(done) or "—", "| übersprungen:", ", ".join(skipped) or "—")
