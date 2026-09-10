#!/usr/bin/env python3
"""Baut 6 clean, ad-safe Ad-Reels (produktfokus) aus product_pool.json.
Keine Modelle/Haut (kein Adult-Flag), keine Marken-Look-Produkte (kein Counterfeit-Flag),
keine Claims. Output: content/ads/LuxeStyle_AdClean_<Theme>.mp4"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
POOL = json.load(open(os.path.join(HERE, "product_pool.json"), encoding="utf-8"))["products"]
ADS = os.path.normpath(os.path.join(HERE, "..", "ads"))
BY = {p["title"]: p for p in POOL}

BRAND, CODE, DOMAIN, ACCENT = "LuxeStyle", "WELCOME10", "luxestyle.ch", "#C9A24B"

# 6 Themen — nur cleane, eigene/markenfreie Produkte (Uhren/Smartwatch & Beauty-Serum bewusst raus)
REELS = [
    ("Herren_Leder", {"title": "FÜR IHN", "sub": "Echtleder aus der Schweiz 🇨🇭"}, "calm",
     ["Slim Wallet Echtleder", "Herren Lederarmband Anker", "Bart-Pflegeset Premium"]),
    ("Sommer_Accessoires", {"title": "SOMMER 2026", "sub": "Bereit für draussen ☀️"}, "upbeat",
     ["Retro Sonnenbrille Polarisiert", "Crossbody-Bag Vegan", "XL Strandtuch Bio-Baumwolle"]),
    ("Wellness_Zuhause", {"title": "ZUHAUSE WOHLFÜHLEN", "sub": "Ruhe & Ambiente"}, "calm",
     ["Aroma Diffuser Bambus 500ml", "Himalaya Salzkristall-Lampe", "Seiden-Kissenbezug 100% Seide"]),
    ("Tech_Audio", {"title": "TECH & SOUND", "sub": "Smart & kabellos"}, "upbeat",
     ["Bluetooth Kopfhörer ANC", "Bluetooth Speaker 360°", "3-in-1 Wireless Charger 15W"]),
    ("FuerSie_Schmuck", {"title": "FÜR SIE", "sub": "Schmuck & Accessoires"}, "calm",
     ["Damen-Armband Edelstahl", "Damen Ohrring-Set 925", "Damen Portemonnaie XL Leder"]),
    ("Ambiente_Licht", {"title": "DEIN AMBIENTE", "sub": "Licht & Duft"}, "upbeat",
     ["Flame Diffuser Premium", "Smart Diffuser XXL Bluetooth", "Galaxy Aurora LED-Projektor"]),
]


def build(theme, hook, music, titles, only_check=False):
    mix = [BY[t] for t in titles]
    cfg = {
        "brand": BRAND, "code": CODE, "domain": DOMAIN, "accent": ACCENT,
        "music": music, "price_badge": True, "progress_bar": True,
        "transition": 0.3, "endcard_dur": 2.4,
        "hook": {"src": mix[0]["src"], "title": hook["title"], "sub": hook["sub"], "dur": 1.9},
        "items": [{"src": p["src"], "title": p["title"], "sub": p["sub"],
                   "dur": 1.9, "zoom": ("in" if i % 2 == 0 else "out"), "fgw": p.get("fgw", 1600)}
                  for i, p in enumerate(mix)],
    }
    out = os.path.join(ADS, f"LuxeStyle_AdClean_{theme}.mp4")
    cfgp = out + ".cfg.json"
    json.dump(cfg, open(cfgp, "w", encoding="utf-8"), ensure_ascii=False)
    rc = subprocess.call([sys.executable, os.path.join(HERE, "build_reel.py"), cfgp, "--out", out])
    try: os.remove(cfgp)
    except OSError: pass
    ok = rc == 0 and os.path.exists(out)
    print(("✓" if ok else "✗"), out, (str(os.path.getsize(out)//1024)+" KB") if ok else "FEHLER")
    return ok


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    targets = REELS if which == "all" else [r for r in REELS if r[0] == which]
    fails = [r[0] for r in targets if not build(*r)]
    sys.exit(1 if fails else 0)
