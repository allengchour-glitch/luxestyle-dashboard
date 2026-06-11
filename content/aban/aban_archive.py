#!/usr/bin/env python3
"""
aban news Pro — Archiv-Generator (SEO-Motor).

Baut aus den taeglichen JSON-Ausgaben in out/ eine oeffentliche Uebersichtsseite
(out/index.html). Jede vergangene Ausgabe wird verlinkt + die Insight-Zeile als
Teaser angezeigt → veroeffentlichbar als /archiv/ → Google-Traffic → neue Abonnenten.

Reine Standardbibliothek. Liest nur die Pro-JSONs (aban-YYYY-MM-DD.json), nicht die -free.

Nutzung:
    python aban_archive.py                 # baut out/index.html aus out/*.json
    python aban_archive.py --out out --title "aban news Archiv"
"""
import os, re, glob, json, html, argparse
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ACCENT, DARK, URL = "#0b5", "#10131a", "https://abannews.com"


def load_issues(out_dir):
    issues = []
    for p in glob.glob(os.path.join(out_dir, "aban-*.json")):
        if p.endswith("-free.json"):
            continue
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        d["_html"] = os.path.basename(p)[:-5] + ".html"
        issues.append(d)
    issues.sort(key=lambda d: d.get("date", ""), reverse=True)
    return issues


def render(issues, title):
    esc = lambda s: html.escape(s or "")
    cards = []
    for d in issues:
        try:
            ds = datetime.strptime(d.get("date", ""), "%Y-%m-%d").strftime("%d.%m.%Y")
        except Exception:
            ds = d.get("date", "")
        teaser = esc((d.get("insight") or "")[:160])
        n = len(d.get("items", []))
        m = d.get("market") or {}
        market = (" · BTC %s" % esc(m.get("btc_str", ""))) if m.get("btc_str") else ""
        cards.append(
            '<a href="%s" style="display:block;text-decoration:none;background:#fff;border:1px solid #e9ecf1;'
            'border-radius:12px;padding:18px 20px;margin-bottom:14px">'
            '<div style="font:700 12px -apple-system,Segoe UI,sans-serif;color:%s;letter-spacing:1px">%s · %d Themen%s</div>'
            '<div style="font:400 15px/1.5 -apple-system,Segoe UI,sans-serif;color:#3a4150;margin-top:6px">%s</div>'
            '</a>' % (esc(d["_html"]), ACCENT, ds, n, market, teaser))
    return (
        '<!doctype html><html lang="de"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>%s</title><meta name="description" content="Taegliches KI- & Krypto-Archiv von aban news (DACH, Deutsch).">'
        '</head><body style="margin:0;background:#eef1f5;font-family:-apple-system,Segoe UI,sans-serif">'
        '<div style="max-width:680px;margin:0 auto;padding:28px 16px">'
        '<div style="font:800 24px -apple-system,Segoe UI,sans-serif;color:%s;margin-bottom:4px">aban<span style="color:%s">news</span> · Archiv</div>'
        '<div style="color:#8a93a3;font-size:14px;margin-bottom:20px">Jeden Tag KI &amp; Krypto in 5 Minuten — '
        '<a href="%s" style="color:%s">abonnieren</a>.</div>%s'
        '<div style="text-align:center;color:#9aa3b2;font-size:12px;margin-top:24px">%d Ausgaben · aban news</div>'
        '</div></body></html>'
    ) % (esc(title), DARK, ACCENT, esc(URL), ACCENT, "".join(cards) or "<p>Noch keine Ausgaben.</p>", len(issues))


def main():
    ap = argparse.ArgumentParser(description="aban news Pro — Archiv-Index bauen")
    ap.add_argument("--out", default=os.path.join(HERE, "out"), help="Ordner mit den Ausgaben")
    ap.add_argument("--title", default="aban news — KI & Krypto Archiv")
    args = ap.parse_args()
    issues = load_issues(args.out)
    path = os.path.join(args.out, "index.html")
    open(path, "w", encoding="utf-8").write(render(issues, args.title))
    print("✓ Archiv: %s (%d Ausgaben)" % (path, len(issues)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
