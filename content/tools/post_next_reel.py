#!/usr/bin/env python3
"""
Postet **1 von 6 ad-safe Reels** (rotierend nach Stunde) als **Video** auf Telegram
via social_post.py. Für die stündliche GitHub-Action (luxestyle-reels-hourly.yml).

Rotation: Reel-Index = aktuelle UTC-Stunde mod 6 (oder ENV REEL_INDEX). So kommt
jede Stunde ein anderes der 6 Reels; nach 6 h beginnt der Zyklus von vorn.

Kanal: Telegram (einziger offener Auto-Post-Weg). TikTok/IG bleiben Hand-Upload
bzw. Buffer (siehe content/BROWSER_CLAUDE_BUFFER_POSTING.md).

ENV: TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID (als Secret, nie im Chat/Git).
"""
import os, subprocess, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ADS = os.path.normpath(os.path.join(HERE, "..", "ads"))

REELS = [
    ("LuxeStyle_Sommer_AdSafe.mp4", "Sommer-Mix"),
    ("LuxeStyle_FuerSie_AdSafe.mp4", "Für Sie – Schmuck & Accessoires"),
    ("LuxeStyle_Tech_AdSafe.mp4", "Tech & Gadgets"),
    ("LuxeStyle_Wellness_AdSafe.mp4", "Wellness & Zuhause"),
    ("LuxeStyle_Reise_AdSafe.mp4", "Sommer & Reise"),
    ("LuxeStyle_Geschenke_Ihn_AdSafe.mp4", "Geschenke für Ihn"),
]

if not (os.environ.get("TELEGRAM_BOT_TOKEN") and os.environ.get("TELEGRAM_CHAT_ID")):
    print("⏭️  Übersprungen: TELEGRAM_BOT_TOKEN/CHAT_ID nicht gesetzt "
          "(Repo-Secrets ergänzen, dann postet die Action stündlich).")
    sys.exit(0)

env_idx = os.environ.get("REEL_INDEX")
idx = (int(env_idx) if env_idx not in (None, "") else datetime.now(timezone.utc).hour) % len(REELS)
fname, theme = REELS[idx]
path = os.path.join(ADS, fname)
if not os.path.exists(path):
    sys.exit("Reel fehlt: " + path)

text = ("✨ LuxeStyle – %s\n"
        "Premium aus der Schweiz 🇨🇭 · 10%% mit Code WELCOME10 🛍️\n"
        "#luxestyle #swissmade #schweiz #sommer2026 #shopping #geschenkidee" % theme)

print("→ Poste Reel #%d: %s (%s)" % (idx, fname, theme))
rc = subprocess.call([sys.executable, os.path.join(HERE, "social_post.py"),
                      "--video", path, "--text", text, "--link", "https://luxestyle.ch"])
sys.exit(rc)
