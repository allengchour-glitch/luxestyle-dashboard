#!/usr/bin/env python3
"""
LuxeStyle Auto-Zyklus  —  ein Lauf der Reel-Automation (für stündliche GitHub-Action).

Was ein Lauf macht:
  1) ROTIERT einen frischen Produkt-Mix aus product_pool.json (jede Stunde anders
     -> mehr & andere Gegenstände, keine Wiederholung).
  2) BAUT daraus ein Premium-9:16-Reel via build_reel.py (alternierende Musik/Hooks).
  3) LERNT: liest – falls vorhanden – den neuesten TikTok-Analyse-Report
     (content/reports/tiktok_*.json von tiktok_analyze.py) und übernimmt Top-Hashtags
     + bestperformenden Hook in die nächste Caption/den Hook.
  4) POSTET einen **Text-Status** (KEIN Video) auf Telegram & Co. via social_post.py
     – das eigentliche Reel-Video wird NICHT pro Stunde verschickt (Anti-Spam);
     es liegt als Datei/Artefakt zum manuellen TikTok-Upload bereit.

Variety-Logik: Rotations-Offset = Stunden seit Epoch (oder --offset). So bekommt
jeder Lauf einen anderen, fortlaufenden Ausschnitt des Pools.

Nutzung:
  python auto_cycle.py                          # ein Zyklus, default 4 Produkte
  python auto_cycle.py --count 5 --analyze      # vorher TikTok-Analyse (Lernen)
  python auto_cycle.py --no-post                # nur bauen, nichts posten
  python auto_cycle.py --offset 7               # festen Mix wählen (Test)

Nur Standardbibliothek; ruft build_reel.py / tiktok_analyze.py / social_post.py auf.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
POOL = os.path.join(HERE, "product_pool.json")
REPORTS = os.path.normpath(os.path.join(HERE, "..", "reports"))

BRAND = "LuxeStyle"
CODE = "WELCOME10"
DOMAIN = "luxestyle.ch"
ACCENT = "#C9A24B"

# Rotierende Hooks (Fallback, falls keine Lern-Daten). Premium, kein Billig-Claim.
HOOKS = [
    {"title": "SOMMER 2026", "sub": "Premium aus der Schweiz 🇨🇭"},
    {"title": "NEU ENTDECKT", "sub": "Looks für sie & ihn"},
    {"title": "GESCHENK GESUCHT?", "sub": "Mit Code WELCOME10"},
    {"title": "BESTSELLER", "sub": "Versand aus der Schweiz"},
    {"title": "DAILY DROP", "sub": "-10% mit WELCOME10"},
]


def load_pool():
    with open(POOL, encoding="utf-8") as f:
        return json.load(f)["products"]


def latest_report():
    """Neuesten tiktok_*.json-Report finden -> (top_hashtags[list], best_hook[str|None])."""
    cands = sorted(glob.glob(os.path.join(REPORTS, "tiktok_*.json")))
    if not cands:
        return [], None
    try:
        with open(cands[-1], encoding="utf-8") as f:
            rep = json.load(f).get("report", {})
        tags = ["#" + h["tag"] for h in rep.get("hashtags_ranked", [])[:4]]
        tops = rep.get("top_by_views", [])
        hook = None
        if tops and tops[0].get("caption"):
            hook = tops[0]["caption"][:32].strip()
        return tags, hook
    except Exception:
        return [], None


def pick_mix(products, count, offset):
    """Fortlaufender, wrappender Ausschnitt -> jede Stunde ein anderer Mix.
    Ad-restricted Produkte (z.B. Beauty mit Health-Claims) werden ausgeschlossen."""
    products = [p for p in products if not p.get("ad_restricted")]
    n = len(products)
    count = min(count, n)
    idx = [(offset + i) % n for i in range(count)]
    return [products[i] for i in idx]


def build_reel(mix, music, hook, out_path):
    cfg = {
        "brand": BRAND, "code": CODE, "domain": DOMAIN, "accent": ACCENT,
        "music": music, "price_badge": True, "progress_bar": True,
        "transition": 0.3, "endcard_dur": 2.4,
        "hook": {"src": mix[0]["src"], "title": hook["title"], "sub": hook["sub"], "dur": 1.9},
        "items": [
            {"src": p["src"], "title": p["title"], "sub": p["sub"],
             "dur": 1.8, "zoom": ("in" if i % 2 == 0 else "out"), "fgw": p.get("fgw", 1600)}
            for i, p in enumerate(mix)
        ],
        # Ad-safe: KEINE Bewertungs-/Health-Claim-Karte (TikTok lehnt unbelegte Claims ab).
        # Reihenfolge bleibt Hook -> Produkte -> End-Card (Marke + WELCOME10 + Domain).
    }
    cfg_path = out_path + ".cfg.json"
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False)
    rc = subprocess.call([sys.executable, os.path.join(HERE, "build_reel.py"), cfg_path, "--out", out_path])
    try:
        os.remove(cfg_path)
    except OSError:
        pass
    return rc == 0 and os.path.exists(out_path)


def main() -> int:
    ap = argparse.ArgumentParser(description="LuxeStyle: ein Auto-Zyklus (bauen + lernen + Text-Status).")
    ap.add_argument("--count", type=int, default=4, help="Produkte pro Reel (Default 4)")
    ap.add_argument("--offset", type=int, default=None, help="Rotations-Offset (Default: Stunden seit Epoch)")
    ap.add_argument("--out-dir", default=os.path.normpath(os.path.join(HERE, "..", "ads", "auto")))
    ap.add_argument("--analyze", action="store_true", help="vorher TikTok-Analyse laufen lassen (Lernen)")
    ap.add_argument("--no-post", action="store_true", help="kein Telegram-Text-Status")
    args = ap.parse_args()

    products = load_pool()
    offset = args.offset if args.offset is not None else int(time.time() // 3600)

    # 1) Lernen (optional): Analyse aktualisieren
    if args.analyze:
        os.makedirs(REPORTS, exist_ok=True)
        print("→ TikTok-Analyse (Lernen) ...")
        subprocess.call([sys.executable, os.path.join(HERE, "tiktok_analyze.py"), "--out", REPORTS])

    top_tags, learned_hook = latest_report()

    # 2) Mix + Hook wählen
    mix = pick_mix(products, args.count, offset)
    hook = dict(HOOKS[offset % len(HOOKS)])
    if learned_hook:
        hook = {"title": "TOP DIESE WOCHE", "sub": learned_hook}
    music = "upbeat" if offset % 2 == 0 else "calm"

    os.makedirs(args.out_dir, exist_ok=True)
    stamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M")
    out_path = os.path.join(args.out_dir, f"LuxeStyle_auto_{stamp}.mp4")

    print(f"→ Mix (offset {offset}): " + ", ".join(p["title"] for p in mix))
    print(f"→ Musik: {music} · Hook: {hook['title']} / {hook['sub']}")
    ok = build_reel(mix, music, hook, out_path)
    if not ok:
        sys.stderr.write("! Reel-Bau fehlgeschlagen.\n")
        return 1
    size_kb = os.path.getsize(out_path) // 1024
    print(f"✓ Reel: {out_path} ({size_kb} KB)")

    # 4) Text-Status posten (KEIN Video)
    names = " · ".join(p["title"] for p in mix)
    tag_line = (" " + " ".join(top_tags)) if top_tags else " #luxestyle #schweiz #sommer2026"
    text = (f"🆕 Neues LuxeStyle-Reel ist fertig ({datetime.now().strftime('%H:%M')}).\n"
            f"Heute im Mix: {names}.\n"
            f"🎁 10% mit Code {CODE} · Versand aus der Schweiz 🇨🇭{tag_line}")
    if args.no_post:
        print("\n(--no-post: kein Status gesendet)\n— Text wäre gewesen —\n" + text)
    else:
        print("→ Text-Status (kein Video) ...")
        subprocess.call([sys.executable, os.path.join(HERE, "social_post.py"),
                         "--text", text, "--link", f"https://{DOMAIN}"])

    # Lern-/Lauf-Log (klein, im Repo nachvollziehbar)
    os.makedirs(REPORTS, exist_ok=True)
    with open(os.path.join(REPORTS, "auto_log.md"), "a", encoding="utf-8") as f:
        f.write(f"- {stamp} · offset {offset} · {music} · {names} · {os.path.basename(out_path)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
