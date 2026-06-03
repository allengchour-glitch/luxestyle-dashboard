#!/usr/bin/env python3
"""
LuxeStyle Mehrkanal-Publisher  —  postet ein Reel (oder Text) auf Telegram & Co.,
gratis, ohne Make/Zapier. Nur Standardbibliothek (urllib).

Kanäle (alle optional, je per ENV-Secret aktiviert; nicht gesetzt = übersprungen):
    TELEGRAM_BOT_TOKEN   = 123456:ABC...          (von @BotFather)
    TELEGRAM_CHAT_ID     = @deinkanal  ODER  numerische Chat-ID
    DISCORD_WEBHOOK_URL  = https://discord.com/api/webhooks/...
    PUBLISH_WEBHOOK_URL  = generischer Webhook (POST JSON) -> Make/n8n/Zapier
                           -> fächert weiter an IG/X/LinkedIn (deren APIs gehen
                           nicht sauber direkt aus einem Skript).

Mit --video wird das **Reel selbst** hochgeladen (Telegram sendVideo / Discord
File-Upload). Ohne --video nur Text + Link (sendMessage).

SICHERHEIT: Tokens stehen NIE im Code/Git — nur aus Umgebungsvariablen.
Den Bot-Token NICHT in den Chat schreiben, sondern als ENV/Secret setzen.

Nutzung:
    # Reel auf Telegram posten (Caption + Shop-Link)
    python social_post.py --video ../ads/LuxeStyle_EU_Hero_Reel.mp4
    # eigener Text/Link
    python social_post.py --text "Sommer-Drop ist live ✨" --link https://luxestyle.ch
    # nur anzeigen, was gesendet würde
    python social_post.py --video ../ads/LuxeStyle_Mix_Reel_Sommer.mp4 --dry-run

Telegram-Setup (einmalig, Browser/Handy):
    1) In Telegram @BotFather -> /newbot -> Token kopieren  -> TELEGRAM_BOT_TOKEN
    2) Bot in deinen Kanal/deine Gruppe als Admin packen (oder ihm schreiben)
    3) Chat-ID: bei Kanal "@meinkanal", sonst numerische ID  -> TELEGRAM_CHAT_ID
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

# Standard-Caption (premium, clean) + Shop-Link. Per --text/--link überschreibbar.
DEFAULT_TEXT = (
    "✨ LuxeStyle — Sommer 2026 ist da.\n"
    "Schmuck der nicht anläuft · Looks für sie & ihn · Versand aus der Schweiz 🇨🇭\n"
    "🎁 10% mit Code WELCOME10"
)
DEFAULT_LINK = "https://luxestyle.ch"


def _multipart(fields, files):
    """fields: dict[str,str]; files: dict[name,(filename,bytes,ctype)] -> (body, content_type)."""
    import hashlib
    boundary = "----luxe" + hashlib.md5(os.urandom(8)).hexdigest()
    b = bytearray()
    for k, v in fields.items():
        b += ("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n"
              % (boundary, k, v)).encode("utf-8")
    for k, (fname, content, ctype) in files.items():
        b += ("--%s\r\nContent-Disposition: form-data; name=\"%s\"; filename=\"%s\"\r\n"
              "Content-Type: %s\r\n\r\n" % (boundary, k, fname, ctype)).encode("utf-8")
        b += content + b"\r\n"
    b += ("--%s--\r\n" % boundary).encode("utf-8")
    return bytes(b), "multipart/form-data; boundary=" + boundary


def send_telegram(text, link=None, video=None):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not (token and chat):
        return None
    caption = text + (f"\n{link}" if link else "")
    if video:
        with open(video, "rb") as f:
            content = f.read()
        fields = {"chat_id": chat, "caption": caption, "supports_streaming": "true"}
        files = {"video": (os.path.basename(video), content, "video/mp4")}
        body, ctype = _multipart(fields, files)
        api = f"https://api.telegram.org/bot{token}/sendVideo"
        req = urllib.request.Request(api, data=body, headers={"Content-Type": ctype})
    else:
        api = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": chat, "text": caption,
                                       "disable_web_page_preview": "false"}).encode("utf-8")
        req = urllib.request.Request(api, data=data)
    with urllib.request.urlopen(req, timeout=180) as r:
        out = json.loads(r.read())
    return bool(out.get("ok"))


def send_discord(text, link=None, video=None):
    url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not url:
        return None
    body_text = text + (f"\n{link}" if link else "")
    if video:
        with open(video, "rb") as f:
            content = f.read()
        fields = {"content": body_text}
        files = {"file": (os.path.basename(video), content, "video/mp4")}
        data, ctype = _multipart(fields, files)
        req = urllib.request.Request(url, data=data, headers={"Content-Type": ctype})
    else:
        data = json.dumps({"content": body_text}).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.status in (200, 201, 204)


def send_webhook(text, link=None, video=None):
    """Generischer Fan-out an Make/n8n/Zapier (Video als Pfad-Referenz, kein Upload)."""
    url = os.environ.get("PUBLISH_WEBHOOK_URL")
    if not url:
        return None
    payload = {"text": text, "url": link, "video": video}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status in (200, 201, 204)


CHANNELS = {"telegram": send_telegram, "discord": send_discord, "webhook": send_webhook}


def _is_set(name):
    return {
        "telegram": bool(os.environ.get("TELEGRAM_BOT_TOKEN") and os.environ.get("TELEGRAM_CHAT_ID")),
        "discord": bool(os.environ.get("DISCORD_WEBHOOK_URL")),
        "webhook": bool(os.environ.get("PUBLISH_WEBHOOK_URL")),
    }[name]


def main() -> int:
    ap = argparse.ArgumentParser(description="LuxeStyle: Reel/Text auf Telegram & Co. posten.")
    ap.add_argument("--video", help="Pfad zum Reel-MP4 (wird als Video hochgeladen)")
    ap.add_argument("--text", default=DEFAULT_TEXT, help="Caption/Text (Default: Sommer-Drop)")
    ap.add_argument("--link", default=DEFAULT_LINK, help="Shop-Link (Default luxestyle.ch)")
    ap.add_argument("--dry-run", action="store_true", help="nur anzeigen, nichts senden")
    args = ap.parse_args()

    if args.video and not os.path.exists(args.video):
        sys.exit("Video nicht gefunden: " + args.video)

    print("— Post —")
    print(args.text + (f"\n{args.link}" if args.link else ""))
    if args.video:
        print(f"[Video: {args.video}, {os.path.getsize(args.video) // 1024} KB]")
    print()

    if args.dry_run:
        print("(dry-run — nichts gesendet)")
        return 0

    active = [n for n in CHANNELS if _is_set(n)]
    if not active:
        sys.stderr.write(
            "Kein Kanal konfiguriert. Setze mindestens einen (als ENV/Secret, NICHT im Chat):\n"
            "  TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID\n"
            "  DISCORD_WEBHOOK_URL\n"
            "  PUBLISH_WEBHOOK_URL\n")
        return 2

    print(f"Aktive Kanäle: {', '.join(active)}")
    rc = 0
    for name in active:
        try:
            ok = CHANNELS[name](args.text, args.link, args.video)
            print(f"  {name}: {'✓ gesendet' if ok else '✗ fehlgeschlagen'}")
            if not ok:
                rc = 1
        except Exception as ex:
            print(f"  {name}: ✗ Fehler ({ex})")
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
