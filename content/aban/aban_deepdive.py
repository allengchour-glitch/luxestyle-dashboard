#!/usr/bin/env python3
"""
aban news Pro — Wochen-Deep-Dive (Pro-exklusiv).

Das staerkste Pro-Argument: eine woechentliche Langanalyse. Liest die Tages-Ausgaben
der letzten 7 Tage (out/aban-YYYY-MM-DD.json), erkennt das **Thema der Woche** und
schreibt einen strukturierten deutschen Deep-Dive (mit ANTHROPIC_API_KEY LLM-veredelt,
sonst sauberer strukturierter Fallback aus den Wochen-Items).

Ausgabe:
    out/aban-deepdive-YYYY-Www.html   (gebrandet, fuer Pro-Mail / Web)
    out/aban-deepdive-YYYY-Www.md
    out/aban-deepdive-YYYY-Www.json

Nutzung:
    python aban_deepdive.py                 # letzte 7 Tage, auto-Thema
    python aban_deepdive.py --days 7
    python aban_deepdive.py --topic ki      # auf KI/Krypto einschraenken
    python aban_deepdive.py --no-llm

ENV: ANTHROPIC_API_KEY (Veredelung), ABAN_DEEPDIVE_MODEL (Default = starkes Claude-Modell).
"""
import os, re, sys, glob, json, html, argparse, urllib.request
from datetime import datetime, timezone, timedelta
from collections import Counter

import aban_news_pro as E  # Helfer wiederverwenden (BRAND, fetch, clean_text, HOT, _ctx, utm)

HERE = os.path.dirname(os.path.abspath(__file__))
STOP = set("der die das und in im von mit fuer für auf ein eine zu den dem des am ist sind "
           "wird werden bei aus nach als auch noch wie war hat haben sich seine ihre einen einem "
           "the a an of to and in for on is are be with this that uebernimmt mehr neue neuer".split())


def load_week(out_dir, days):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    issues = []
    for p in sorted(glob.glob(os.path.join(out_dir, "aban-*.json"))):
        b = os.path.basename(p)
        if "-free" in b or "deepdive" in b:
            continue
        try:
            d = json.load(open(p, encoding="utf-8"))
            dd = datetime.strptime(d.get("date", ""), "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except Exception:
            continue
        if dd >= cutoff:
            issues.append(d)
    return issues


def collect_items(issues, topic):
    items, seen = [], set()
    for d in issues:
        for it in d.get("items", []):
            if topic and it.get("topic") != topic:
                continue
            k = (it.get("link") or "").split("?")[0]
            if k in seen:
                continue
            seen.add(k)
            items.append(it)
    return items


def week_theme(items):
    """Dominantes Thema der Woche: haeufigste relevante Begriffe (HOT + markante Tokens)."""
    c = Counter()
    for it in items:
        blob = (it.get("title", "") + " " + it.get("summary", "")).lower()
        for k in E.HOT:
            if k in blob:
                c[k] += 2
        for tok in re.findall(r"[a-zaeoeueäöüß]{5,}", blob):
            if tok not in STOP:
                c[tok] += 1
    if not c:
        return "KI & Krypto", []
    top = [w for w, _ in c.most_common(6)]
    label = top[0].upper() if len(top[0]) <= 4 else top[0].capitalize()
    return label, top


def relevant(items, terms, limit=8):
    def hits(it):
        b = (it.get("title", "") + " " + it.get("summary", "")).lower()
        return sum(1 for t in terms if t in b)
    return sorted([it for it in items if hits(it)], key=hits, reverse=True)[:limit] or items[:limit]


# ----------------------------------------------------------------------------- Fallback-Aufbau
def fallback_deepdive(theme, terms, picks, n_total, n_days):
    L = []
    L.append("In den letzten %d Tagen drehte sich bei aban news viel um **%s**. "
             "Aus %d Meldungen der Woche sticht ein Muster heraus — hier die Einordnung." % (n_days, theme, n_total))
    L.append("")
    L.append("## Was diese Woche passiert ist")
    for it in picks:
        L.append("- **%s** (%s): %s" % (it.get("title", ""), it.get("source", ""),
                                        (it.get("summary", "") or "")[:160]))
    L.append("")
    L.append("## Warum es zaehlt")
    L.append("Mehrere unabhaengige Quellen berichten zum selben Strang — ein Zeichen, dass sich hier "
             "kein Einzelfall, sondern ein Trend formt. Fuer DACH-Leser heisst das: Thema aktiv beobachten, "
             "statt es als Tagesrauschen abzutun. Wer frueh versteht, kann Werkzeuge testen oder Positionen "
             "anpassen, bevor es Mainstream wird.")
    L.append("")
    L.append("## Worauf jetzt achten")
    L.append("- Folgemeldungen der naechsten Tage zu den genannten Akteuren")
    L.append("- Reaktionen aus Regulierung/Markt (EU/DACH) auf die Entwicklung")
    L.append("- Konkrete Verfuegbarkeit/Preise — wann es vom Konzept zum nutzbaren Produkt wird")
    return "\n".join(L)


def llm_deepdive(theme, picks, model):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    src = [{"title": it.get("title"), "source": it.get("source"), "summary": it.get("summary"),
            "topic": it.get("topic")} for it in picks]
    prompt = (
        "Du bist Chefredakteur des deutschen KI-/Krypto-Newsletters 'aban news' (DACH). "
        "Schreibe einen woechentlichen Deep-Dive (450-650 Woerter, Deutsch) zum Thema '%s'. "
        "Struktur in Markdown: kurzer Lead-Absatz, dann ## Was passiert ist, ## Warum es zaehlt, "
        "## Worauf jetzt achten. Sachlich, analytisch, kein Clickbait, konkrete Bezuege zu den Quellen. "
        "Nutze NUR die folgenden Wochen-Meldungen als Basis:\n\n%s\n\nGib NUR den Markdown-Text zurueck."
        % (theme, json.dumps(src, ensure_ascii=False))
    )
    body = json.dumps({"model": model, "max_tokens": 1800,
                       "messages": [{"role": "user", "content": prompt}]}).encode("utf-8")
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body,
                                 headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                                          "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120, context=E._ctx()) as r:
            data = json.loads(r.read())
        text = "".join(c.get("text", "") for c in data.get("content", []) if c.get("type") == "text").strip()
        return text or None
    except Exception as e:
        print("  ! LLM-Deep-Dive uebersprungen (%s)" % e, file=sys.stderr)
        return None


# ----------------------------------------------------------------------------- Render
def md_to_html(md):
    out, in_ul = [], False
    for line in md.split("\n"):
        if line.startswith("## "):
            if in_ul:
                out.append("</ul>"); in_ul = False
            out.append('<h2 style="font:700 19px Georgia,serif;color:#10131a;margin:22px 0 8px">%s</h2>' % html.escape(line[3:]))
        elif line.startswith("- "):
            if not in_ul:
                out.append('<ul style="margin:0 0 8px;padding-left:20px">'); in_ul = True
            out.append('<li style="font:400 15px/1.6 -apple-system,Segoe UI,sans-serif;color:#3a4150;margin:4px 0">%s</li>' % _inline(line[2:]))
        elif line.strip() == "":
            if in_ul:
                out.append("</ul>"); in_ul = False
        else:
            if in_ul:
                out.append("</ul>"); in_ul = False
            out.append('<p style="font:400 15px/1.65 -apple-system,Segoe UI,sans-serif;color:#3a4150;margin:8px 0">%s</p>' % _inline(line))
    if in_ul:
        out.append("</ul>")
    return "\n".join(out)


def _inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return s


def render_html(theme, body_md, week_label, n_total):
    a, dark = E.BRAND["accent"], E.BRAND["dark"]
    return (
        '<!doctype html><html lang="de"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>aban Deep Dive — %s</title></head>'
        '<body style="margin:0;background:#eef1f5;padding:24px 0">'
        '<table role="presentation" width="100%%" cellpadding="0" cellspacing="0"><tr><td align="center">'
        '<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%%;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 8px 30px rgba(16,19,26,.08)">'
        '<tr><td style="background:%s;padding:24px 28px">'
        '<div style="font:700 11px -apple-system,Segoe UI,sans-serif;letter-spacing:2px;text-transform:uppercase;color:#bdf5d6">aban Pro · Deep Dive</div>'
        '<div style="font:800 22px Georgia,serif;color:#fff;margin-top:6px">%s</div>'
        '<div style="font:400 13px -apple-system,Segoe UI,sans-serif;color:#aeb6c4;margin-top:6px">Woche %s · Basis: %d Meldungen</div>'
        '</td></tr>'
        '<tr><td style="padding:6px 28px 24px">%s</td></tr>'
        '<tr><td style="padding:18px 28px;background:#fafbfc;text-align:center">'
        '<div style="font:400 13px -apple-system,Segoe UI,sans-serif;color:#8a93a3">Exklusiv fuer aban Pro · jede Woche eine Tiefenanalyse.</div>'
        '<a href="%s" style="display:inline-block;margin-top:12px;background:%s;color:#fff;font:700 14px -apple-system,Segoe UI,sans-serif;text-decoration:none;padding:11px 22px;border-radius:8px">aban.news</a>'
        '</td></tr></table></td></tr></table></body></html>'
    ) % (html.escape(theme), dark, html.escape(theme), html.escape(week_label), n_total,
         md_to_html(body_md), E.utm(E.BRAND["url"], "deepdive"), a)


def main():
    ap = argparse.ArgumentParser(description="aban news Pro — Wochen-Deep-Dive")
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--topic", choices=["ki", "krypto"], help="auf ein Thema einschraenken")
    ap.add_argument("--no-llm", action="store_true")
    ap.add_argument("--model", default=os.environ.get("ABAN_DEEPDIVE_MODEL", "claude-sonnet-4-6"))
    args = ap.parse_args()

    issues = load_week(args.out, args.days)
    if not issues:
        print("Keine Tages-Ausgaben der letzten %d Tage gefunden — erst aban_news_pro.py laufen lassen." % args.days, file=sys.stderr)
        return 1
    items = collect_items(issues, args.topic)
    theme, terms = week_theme(items)
    picks = relevant(items, terms, 8)
    print("aban Deep-Dive — Thema: %s (%d Wochen-Meldungen, %d Ausgaben)" % (theme, len(items), len(issues)))

    body = None if args.no_llm else llm_deepdive(theme, picks, args.model)
    used_llm = bool(body)
    if not body:
        body = fallback_deepdive(theme, terms, picks, len(items), args.days)

    now = datetime.now(timezone.utc).astimezone()
    iso = now.isocalendar()
    week_label = "%04d-W%02d" % (iso[0], iso[1])
    base = os.path.join(args.out, "aban-deepdive-%s" % week_label)
    open(base + ".html", "w", encoding="utf-8").write(render_html(theme, body, week_label, len(items)))
    open(base + ".md", "w", encoding="utf-8").write("# aban Deep Dive — %s (Woche %s)\n\n%s\n" % (theme, week_label, body))
    json.dump({"week": week_label, "theme": theme, "terms": terms, "llm": used_llm,
               "based_on": len(items), "generated": now.isoformat(),
               "sources": [{"title": it.get("title"), "link": it.get("link"), "source": it.get("source")} for it in picks]},
              open(base + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print("✓ Deep-Dive: %s.html/.md/.json · LLM:%s" % (base, "an" if used_llm else "aus (Fallback)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
