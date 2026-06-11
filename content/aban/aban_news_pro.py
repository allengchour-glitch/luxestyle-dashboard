#!/usr/bin/env python3
"""
aban news Pro — taeglicher KI- & Krypto-Digest-Generator (DACH, Deutsch).

Holt die wichtigsten KI- und Krypto-News des Tages aus kuratierten RSS/Atom-Quellen,
dedupliziert, rankt, holt den **Volltext** der Top-Artikel, fasst auf Deutsch im
5-Minuten-Format zusammen und baut eine **versandfertige** Ausgabe:

    out/aban-YYYY-MM-DD.html   (E-Mail-/Web-ready, gebrandet)
    out/aban-YYYY-MM-DD.md     (Markdown, z.B. fuer Blog/Substack)
    out/aban-YYYY-MM-DD.txt    (Plaintext-Fallback)
    out/aban-YYYY-MM-DD.json   (strukturierte Items, fuer Versand/Analytics)

WAS ES EINZIGARTIG MACHT ("nur bei aban news"):
  - **Markt-Snapshot** oben (BTC/ETH live, keyless) — Newsletter + Marktblick in einem
  - **"aban Insight"**: eine taegliche Synthese-Zeile, die die Lage in einem Satz einordnet
  - jede Story mit Zeile **"Was es bedeutet"** (praktische DACH-Einordnung statt nur Schlagzeile)
  - taeglicher **"aban Pick"** (Tool/Coin/Thema des Tages)
  - **Volltext-Zusammenfassung** (trafilatura) statt magerer Feed-Snippets
  - DACH-fokussiert, deutsch, KI+Krypto in EINER 5-Min-Mail — so gebuendelt gibt es das nur hier.

ABHAENGIGKEITEN (alle optional, mit sauberem stdlib-Fallback → laeuft auch ohne):
  feedparser    robustes Feed-Parsing          (sonst: eingebauter XML-Parser)
  trafilatura   Volltext-Extraktion            (sonst: Feed-Snippet)
  langdetect    Sprach-Tag/-Filter             (sonst: kein Filter)
  ANTHROPIC_API_KEY  LLM-Veredelung (DE-Summary+Einordnung+Insight)  (sonst: Heuristik/Extraktiv)

Installation der Extras:
  SETUPTOOLS_USE_DISTUTILS=stdlib pip install feedparser trafilatura langdetect

Nutzung:
    python aban_news_pro.py                      # KI+Krypto, 8 Stories, out/
    python aban_news_pro.py --check-feeds        # nur Quellen-Gesundheit pruefen
    python aban_news_pro.py --topics ki --max 6  # nur KI, 6 Stories
    python aban_news_pro.py --no-fulltext        # Volltext-Holen aus (schneller)
    python aban_news_pro.py --no-llm             # LLM-Veredelung erzwungen aus
    python aban_news_pro.py --hours 36           # Zeitfenster (Default 30h)

SICHERHEIT: Keys stehen NIE im Code — nur aus Umgebungsvariablen (ANTHROPIC_API_KEY).
Portierbar: in jedem Repo lauffaehig (z.B. aban-news-landing).
"""
import os, re, sys, json, ssl, html, argparse, urllib.request, urllib.parse, urllib.error
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET

# ---- optionale Extras (graceful) -------------------------------------------
try:
    import feedparser
except Exception:
    feedparser = None
try:
    import trafilatura
except Exception:
    trafilatura = None
try:
    from langdetect import detect as _lang_detect
except Exception:
    _lang_detect = None

UA = "Mozilla/5.0 (aban-news-pro/1.1; +https://abannews.com)"
BRAND = {"name": "aban news", "accent": "#0b5", "dark": "#10131a", "url": "https://abannews.com"}
HERE_DIR = os.path.dirname(os.path.abspath(__file__))

# Kuratierte Quellen je Thema: (Anzeigename, Feed-URL, Gewicht 1-3).
# Gewicht = Qualitaet/DACH-Relevanz; fliesst ins Ranking ein. (Stand 2026-06, live geprueft.)
SOURCES = {
    "ki": [
        ("The Decoder", "https://the-decoder.de/feed/", 3),
        ("t3n", "https://t3n.de/rss.xml", 3),
        ("heise online", "https://www.heise.de/rss/heise-atom.xml", 2),
        ("OpenAI Blog", "https://openai.com/blog/rss.xml", 2),
        ("Google DeepMind", "https://deepmind.google/blog/rss.xml", 2),
        ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/", 1),
        ("MIT Tech Review", "https://www.technologyreview.com/feed/", 1),
    ],
    "krypto": [
        ("BTC-ECHO", "https://www.btc-echo.de/feed/", 3),
        ("Blocktrainer", "https://www.blocktrainer.de/feed/", 3),
        ("Cointelegraph", "https://cointelegraph.com/rss", 2),
        ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/", 2),
        ("Decrypt", "https://decrypt.co/feed", 1),
    ],
}

# Schlagwoerter, die eine Story "wichtig" machen (Ranking-Boost).
HOT = ["gpt", "openai", "anthropic", "claude", "gemini", "llama", "mistral", "agent",
       "ki-gesetz", "ai act", "eu", "nvidia", "chip", "bitcoin", "etf", "ethereum",
       "halving", "sec", "regulierung", "milliard", "billion", "launch", "release",
       "datenschutz", "open source", "deutschland", "schweiz", "österreich", "dach"]

CAMPAIGN = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")


# ----------------------------------------------------------------------------- Netz
def _ctx():
    """SSL-Kontext: respektiert eine evtl. Proxy-CA (SSL_CERT_FILE/NODE_EXTRA_CA_CERTS)."""
    ca = os.environ.get("SSL_CERT_FILE") or os.environ.get("NODE_EXTRA_CA_CERTS")
    try:
        if ca and os.path.exists(ca):
            return ssl.create_default_context(cafile=ca)
        return ssl.create_default_context()
    except Exception:
        return ssl.create_default_context()


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml, text/xml, */*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
            return r.read()
    except Exception:
        try:  # zweiter Versuch ohne strikte Zertifikatspruefung (Proxy bricht TLS gelegentlich)
            unv = ssl.create_default_context(); unv.check_hostname = False; unv.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(req, timeout=timeout, context=unv) as r:
                return r.read()
        except Exception as e2:
            print("  ! Quelle fehlgeschlagen: %s (%s)" % (url, e2), file=sys.stderr)
            return None


def fetch_json(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
            return json.loads(r.read())
    except Exception:
        return None


# ----------------------------------------------------------------------------- Reinigung
_BOILERPLATE = [
    r"Der (Artikel|Beitrag)\b.*?(erschien|erschienen).*?$",
    r"The post\b.*?appeared first on.*?$",
    r"(Weiterlesen|Read more|Mehr dazu|Zum Artikel)\.?\s*$",
    r"Dieser Artikel.*?erschien zuerst.*?$",
]


def strip_html(s):
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s or "")
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def clean_text(s):
    s = strip_html(s)
    for pat in _BOILERPLATE:
        s = re.sub(pat, "", s, flags=re.I | re.S).strip()
    return re.sub(r"\s+", " ", s).strip()


def first_sentences(text, n=2, limit=260):
    sents = re.split(r"(?<=[.!?])\s+", text or "")
    s = " ".join(sents[:n]).strip()
    if len(s) > limit:
        s = s[:limit - 3].rsplit(" ", 1)[0] + "…"
    return s


def parse_date(s):
    if not s:
        return None
    try:
        d = parsedate_to_datetime(s)
        return d.replace(tzinfo=timezone.utc) if d.tzinfo is None else d
    except Exception:
        for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
            try:
                d = datetime.strptime(s.strip(), fmt)
                return d.replace(tzinfo=timezone.utc) if d.tzinfo is None else d
            except Exception:
                pass
    return None


# ----------------------------------------------------------------------------- Parsing
def parse_with_feedparser(raw, source, topic, weight):
    out = []
    fp = feedparser.parse(raw)
    for e in fp.entries:
        title = clean_text(getattr(e, "title", ""))
        link = getattr(e, "link", "") or ""
        desc = clean_text(getattr(e, "summary", "") or getattr(e, "description", ""))
        pub = None
        for attr in ("published", "updated", "created"):
            if getattr(e, attr, None):
                pub = parse_date(getattr(e, attr)); break
        if not pub and getattr(e, "published_parsed", None):
            try:
                import calendar
                pub = datetime.fromtimestamp(calendar.timegm(e.published_parsed), tz=timezone.utc)
            except Exception:
                pass
        if title and link:
            out.append(_item(title, link, desc, pub, source, topic, weight))
    return out


def parse_with_et(raw, source, topic, weight):
    out = []
    try:
        root = ET.fromstring(raw)
    except Exception:
        return out
    tag = lambda e: e.tag.split("}")[-1]
    items = [e for e in root.iter() if tag(e) == "item"] or [e for e in root.iter() if tag(e) == "entry"]
    for it in items:
        title = link = desc = pub = ""
        for ch in list(it):
            t = tag(ch)
            if t == "title":
                title = (ch.text or "").strip()
            elif t == "link":
                link = ch.get("href") or (ch.text or "").strip() or link
            elif t in ("description", "summary", "content", "encoded") and not desc:
                desc = (ch.text or "").strip()
            elif t in ("pubDate", "published", "updated", "date") and not pub:
                pub = (ch.text or "").strip()
        if title and link:
            out.append(_item(clean_text(title), link.strip(), clean_text(desc), parse_date(pub), source, topic, weight))
    return out


def _item(title, link, desc, pub, source, topic, weight):
    return {"title": title, "link": link, "summary_raw": (desc or "")[:800],
            "published": pub, "source": source, "topic": topic, "weight": weight}


def parse_feed(raw, source, topic, weight):
    if not raw:
        return []
    if feedparser is not None:
        try:
            got = parse_with_feedparser(raw, source, topic, weight)
            if got:
                return got
        except Exception:
            pass
    return parse_with_et(raw, source, topic, weight)


# ----------------------------------------------------------------------------- Dedupe + Rank
def _norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def dedupe(items):
    seen_links, seen_titles, out = set(), [], []
    for it in items:
        lk = it["link"].split("?")[0].rstrip("/")
        if lk in seen_links:
            continue
        nt = set(_norm(it["title"]).split())
        if any(nt and prev and len(nt & prev) / max(1, len(nt | prev)) > 0.6 for prev in seen_titles):
            continue
        seen_links.add(lk)
        seen_titles.append(nt)
        out.append(it)
    return out


def score(it, now):
    s = it["weight"] * 3.0
    if it["published"]:
        age_h = max(0.0, (now - it["published"]).total_seconds() / 3600.0)
        s += max(0.0, 30.0 - age_h) / 5.0
        it["_age_h"] = age_h
    else:
        it["_age_h"] = 999
    blob = (it["title"] + " " + it["summary_raw"]).lower()
    s += sum(1.2 for k in HOT if k in blob)
    if len(it["title"]) > 25:
        s += 0.5
    return s


# ----------------------------------------------------------------------------- Volltext
def enrich_fulltext(items, cap_chars=1200, timeout=12):
    """Holt den Haupttext der ausgewaehlten Artikel (nur diese ~8).
    Nutzt das eigene fetch() mit hartem Timeout (trafilatura.fetch_url hat keinen → kann haengen)."""
    if trafilatura is None:
        return
    for it in items:
        try:
            raw = fetch(it["link"], timeout=timeout)
            if not raw:
                continue
            html_str = raw.decode("utf-8", "ignore") if isinstance(raw, (bytes, bytearray)) else raw
            txt = trafilatura.extract(html_str, include_comments=False, include_tables=False,
                                      favor_precision=True, target_language="de")
            if txt and len(txt) > len(it["summary_raw"]):
                it["fulltext"] = clean_text(txt)[:cap_chars]
        except Exception:
            continue


def detect_lang(it):
    if _lang_detect is None:
        return None
    try:
        return _lang_detect((it["title"] + " " + it["summary_raw"])[:400])
    except Exception:
        return None


# ----------------------------------------------------------------------------- Zusammenfassung
def extractive_summary(it):
    base = it.get("fulltext") or it["summary_raw"] or it["title"]
    return first_sentences(clean_text(base), 2, 260) or it["title"]


# Pro Kategorie: Keywords + mehrere Varianten (rotieren gegen Wiederholung im Heuristik-Modus).
_MEANING_BUCKETS = {
    "krypto_reg": ("etf sec regulier gesetz verbot aufsicht behörde", [
        "Regulatorik bewegt den Markt — wichtig fuer alle, die in Krypto investiert sind.",
        "Aufsicht und Recht setzen den Rahmen — beeinflusst Kurse oft staerker als Technik.",
        "Politische Weichenstellung im Kryptomarkt — die Spielregeln aendern sich gerade."]),
    "krypto_btc": ("bitcoin btc halving miner", [
        "Bitcoin gibt den Takt vor — beobachte, ob Altcoins mitziehen.",
        "BTC-Bewegung faerbt meist auf den Gesamtmarkt ab — Richtung im Blick behalten.",
        "Was bei Bitcoin passiert, zieht oft die ganze Branche nach."]),
    "krypto_eth": ("ethereum eth defi staking layer rollup", [
        "Bewegung im Ethereum-Oekosystem — relevant fuer DeFi/Staking-Strategien.",
        "Ethereum-News treffen DeFi und Layer-2 direkt — fuer Aktive wichtig.",
        "Smart-Contract-Welt im Wandel — kann Renditen und Gebuehren verschieben."]),
    "krypto_gen": ("", [
        "Marktbewegung — kurz einordnen, bevor du handelst.",
        "Ein Signal aus dem Kryptomarkt — Kontext schlaegt Schlagzeile.",
        "Relevant fuer deine Krypto-Strategie — nicht ueberstuerzt reagieren."]),
    "ki_reg": ("gesetz ai act datenschutz eu regulier haftung gericht urteil", [
        "Regulierung entscheidet, welche KI in der EU/DACH erlaubt ist — heute mitdenken.",
        "Rechtlicher Rahmen fuer KI verschiebt sich — betrifft Einsatz im Unternehmen.",
        "Gericht/Gesetzgeber setzen Grenzen — wer KI nutzt, sollte das verfolgen."]),
    "ki_tool": ("open source llama mistral release launch verfügbar update api modell", [
        "Neues Werkzeug zum Ausprobieren — kann deinen Workflow direkt schneller machen.",
        "Frisch verfuegbar — lohnt einen Test, bevor es alle nutzen.",
        "Konkretes Tool/Modell — praktischer Hebel fuer den Alltag."]),
    "ki_agent": ("agent autonom automat workflow assistent", [
        "KI-Agenten uebernehmen mehr Schritte — fruehe Anwender sparen am meisten Zeit.",
        "Automatisierung rueckt naeher — Routineaufgaben lassen sich abgeben.",
        "Agenten-Fortschritt — heute testen heisst morgen Vorsprung."]),
    "ki_money": ("milliard funding bewertung investor runde uebernahme deal", [
        "Kapital fliesst — zeigt, wohin die Branche als Naechstes laeuft.",
        "Grosse Geldbewegung — ein Wegweiser fuer kommende Trends.",
        "Investoren wetten hier — guter Fruehindikator, was wichtig wird."]),
    "ki_gen": ("", [
        "Ein Signal, wohin sich KI bewegt — gut, das auf dem Schirm zu haben.",
        "Entwicklung mit Tragweite — heute einordnen, morgen nutzen.",
        "Relevanter KI-Schritt — Kontext hilft mehr als die blosse Meldung."]),
}


def heuristic_meaning(it, used):
    b = (it["title"] + " " + it["summary_raw"]).lower()
    order = (["krypto_reg", "krypto_btc", "krypto_eth", "krypto_gen"] if it["topic"] == "krypto"
             else ["ki_reg", "ki_tool", "ki_agent", "ki_money", "ki_gen"])
    key = next((k for k in order if _MEANING_BUCKETS[k][0]
                and any(w in b for w in _MEANING_BUCKETS[k][0].split())), order[-1])
    variants = _MEANING_BUCKETS[key][1]
    idx = used.get(key, 0)                       # rotiere je Kategorie durch die Varianten
    used[key] = idx + 1
    return variants[idx % len(variants)]


def llm_enhance(items, model):
    """Anthropic Messages API (urllib, kein SDK): pro Item summary+meaning, plus globaler Insight."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return False, None
    payload = [{"i": i, "topic": it["topic"], "title": it["title"], "src": it["source"],
                "text": (it.get("fulltext") or it["summary_raw"])[:700]} for i, it in enumerate(items)]
    prompt = (
        "Du bist Chefredakteur des deutschen KI-/Krypto-Newsletters 'aban news' (Zielgruppe DACH). "
        "Fuer jeden Eintrag: (1) 'summary' = knackige deutsche Zusammenfassung, 1-2 Saetze, sachlich, "
        "kein Clickbait, max 240 Zeichen; (2) 'meaning' = eine Zeile 'Was es bedeutet', praktische "
        "Einordnung fuer DACH-Leser, max 160 Zeichen, jede Zeile anders. "
        "Ausserdem 'insight' = EIN Satz, der die heutige Gesamtlage einordnet (max 200 Zeichen). "
        "Antworte NUR mit JSON: {\"insight\":\"...\",\"items\":[{\"i\":0,\"summary\":\"...\",\"meaning\":\"...\"}]}\n\n"
        + json.dumps(payload, ensure_ascii=False)
    )
    body = json.dumps({"model": model, "max_tokens": 2200,
                       "messages": [{"role": "user", "content": prompt}]}).encode("utf-8")
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body,
                                 headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                                          "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90, context=_ctx()) as r:
            data = json.loads(r.read())
        text = "".join(c.get("text", "") for c in data.get("content", []) if c.get("type") == "text")
        parsed = json.loads(re.search(r"\{.*\}", text, re.S).group(0))
        for o in parsed.get("items", []):
            i = o.get("i")
            if isinstance(i, int) and 0 <= i < len(items):
                if o.get("summary"):
                    items[i]["summary"] = o["summary"].strip()
                if o.get("meaning"):
                    items[i]["meaning"] = o["meaning"].strip()
        return True, (parsed.get("insight") or "").strip() or None
    except Exception as e:
        print("  ! LLM-Veredelung uebersprungen (%s)" % e, file=sys.stderr)
        return False, None


def heuristic_insight(items, market):
    ki = sum(1 for it in items if it["topic"] == "ki")
    kr = len(items) - ki
    parts = []
    if ki:
        parts.append("%d KI-Themen" % ki)
    if kr:
        parts.append("%d Krypto-Themen" % kr)
    lead = items[0]["title"] if items else ""
    base = "Heute: " + " und ".join(parts) + "."
    if market and market.get("btc"):
        base += " BTC bei %s." % market["btc_str"]
    if lead:
        base += " Top-Thema: %s" % (lead[:90] + ("…" if len(lead) > 90 else ""))
    return base


def pick_of_day(items, used):
    if not items:
        return None
    top = items[0]
    label = "KI-Tool des Tages" if top["topic"] == "ki" else "Krypto-Thema des Tages"
    return {"label": label, "title": top["title"], "link": utm(top["link"]),
            "why": top.get("meaning") or heuristic_meaning(top, used)}


# ----------------------------------------------------------------------------- Markt-Snapshot
def market_snapshot(currency="chf"):
    url = ("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum"
           "&vs_currencies=%s&include_24hr_change=true" % currency)
    data = fetch_json(url)
    if not data or "bitcoin" not in data:
        return None
    cur = currency.upper()
    def fmt(coin):
        p = data[coin][currency]; ch = data[coin].get("%s_24h_change" % currency, 0)
        arrow = "▲" if ch >= 0 else "▼"
        return "%s %s %s (%+.1f%%)" % (cur, ("%.0f" % p if p >= 100 else "%.2f" % p), arrow, ch), ch
    btc_str, btc_ch = fmt("bitcoin")
    eth_str, eth_ch = fmt("ethereum")
    return {"btc": data["bitcoin"][currency], "eth": data["ethereum"][currency],
            "btc_str": btc_str, "eth_str": eth_str, "btc_ch": btc_ch, "eth_ch": eth_ch, "cur": cur}


# ----------------------------------------------------------------------------- UTM
def utm(link, medium="email"):
    sep = "&" if "?" in link else "?"
    q = urllib.parse.urlencode({"utm_source": "abannews", "utm_medium": medium, "utm_campaign": CAMPAIGN})
    return link + sep + q


def reading_time(items):
    words = sum(len((it.get("summary") or "").split()) + 12 for it in items)
    return max(2, round(words / 200))


# ----------------------------------------------------------------------------- Partner / Affiliate
def load_partners(path):
    """Affiliate-/Partner-Slots aus JSON (optional). Fehlt die Datei -> keine Anzeige."""
    try:
        data = json.load(open(path, encoding="utf-8"))
        return [p for p in data.get("partners", []) if p.get("url") and p.get("name")]
    except Exception:
        return None


def pick_partner(partners, lead_topic, day_index):
    """Themenpassenden Partner waehlen (lead_topic bevorzugt), je Tag rotierend."""
    if not partners:
        return None
    pref = [p for p in partners if p.get("topic") in (lead_topic, "any")] or partners
    return pref[day_index % len(pref)]


# ----------------------------------------------------------------------------- Render
def _datestr():
    return datetime.now(timezone.utc).astimezone().strftime("%d.%m.%Y")


def render_md(items, pick, insight, market, mins, cta=None, ad=None):
    L = ["# aban news — KI & Krypto Daily", "", "_%s · in %d Minuten auf dem Laufenden_" % (_datestr(), mins), ""]
    if market:
        L += ["**Markt:** Bitcoin %s · Ethereum %s" % (market["btc_str"], market["eth_str"]), ""]
    if insight:
        L += ["> **aban Insight:** %s" % insight, ""]
    if pick:
        L += ["> **aban Pick — %s:** [%s](%s)  " % (pick["label"], pick["title"], pick["link"]),
              "> %s" % pick["why"], ""]
    cur = None
    for n, it in enumerate(items):
        head = "KI" if it["topic"] == "ki" else "Krypto"
        if head != cur:
            cur = head; L += ["", "## %s" % head, ""]
        L += ["### [%s](%s)" % (it["title"], utm(it["link"])), "*%s*" % it["source"], "",
              it.get("summary") or extractive_summary(it), "",
              "**Was es bedeutet:** %s" % it.get("meaning", ""), ""]
        if ad and n == 1:  # Anzeige mittig zwischen den Stories
            L += ["> _%s_ · **%s** — %s [%s](%s)" % (ad.get("label", "Anzeige"), ad["name"],
                                                     ad.get("blurb", ""), ad.get("cta", "Mehr"), ad["url"]), ""]
    if cta:
        L += ["---", "**%s** — [%s](%s)" % (cta["title"], cta["button"], cta["url"]), cta.get("sub", ""), ""]
    L += ["---", "Taeglich von **aban news** · [abonnieren](%s)" % BRAND["url"]]
    return "\n".join(L)


def render_txt(items, pick, insight, market, mins, cta=None, ad=None):
    L = ["aban news — KI & Krypto Daily", "%s · in %d Minuten" % (_datestr(), mins), ""]
    if market:
        L += ["Markt: BTC %s | ETH %s" % (market["btc_str"], market["eth_str"]), ""]
    if insight:
        L += ["aban Insight: %s" % insight, ""]
    if pick:
        L += ["aban Pick (%s): %s" % (pick["label"], pick["title"]), "  %s" % pick["link"], "  %s" % pick["why"], ""]
    for n, it in enumerate(items, 1):
        L += ["%d. [%s] %s" % (n, "KI" if it["topic"] == "ki" else "Krypto", it["title"]),
              "   Quelle: %s | %s" % (it["source"], utm(it["link"])),
              "   %s" % (it.get("summary") or extractive_summary(it)),
              "   Was es bedeutet: %s" % it.get("meaning", ""), ""]
    if ad:
        L += ["[%s] %s — %s  %s: %s" % (ad.get("label", "Anzeige"), ad["name"], ad.get("blurb", ""),
                                        ad.get("cta", "Mehr"), ad["url"]), ""]
    if cta:
        L += ["--", "%s: %s  %s" % (cta["title"], cta["button"], cta["url"]), ""]
    L += ["--", "Taeglich von aban news · %s" % BRAND["url"]]
    return "\n".join(L)


def render_html(items, pick, insight, market, mins, cta=None, ad=None):
    a, dark = BRAND["accent"], BRAND["dark"]
    esc = lambda s: html.escape(s or "")
    market_html = ""
    if market:
        def chip(label, s, ch):
            col = "#0b5" if ch >= 0 else "#d6452b"
            return ('<td style="padding:0 10px"><span style="font:600 12px -apple-system,Segoe UI,sans-serif;color:#aeb6c4">%s</span> '
                    '<span style="font:700 13px -apple-system,Segoe UI,sans-serif;color:%s">%s</span></td>' % (label, col, esc(s)))
        market_html = ('<tr><td style="padding:0 28px 14px"><table role="presentation"><tr>%s%s</tr></table></td></tr>'
                       % (chip("BTC", market["btc_str"], market["btc_ch"]), chip("ETH", market["eth_str"], market["eth_ch"])))
    insight_html = ""
    if insight:
        insight_html = ('<tr><td style="padding:6px 28px 14px"><div style="font:400 14px/1.5 -apple-system,Segoe UI,sans-serif;'
                        'color:#3a4150;border-left:3px solid %s;padding:6px 0 6px 12px"><b style="color:%s">aban Insight:</b> %s</div></td></tr>'
                        % (a, a, esc(insight)))
    rows, cur = [], None
    for it in items:
        head = "Kuenstliche Intelligenz" if it["topic"] == "ki" else "Krypto & Web3"
        if head != cur:
            cur = head
            rows.append('<tr><td style="padding:24px 28px 4px"><div style="font:700 12px/1 -apple-system,Segoe UI,sans-serif;letter-spacing:2px;text-transform:uppercase;color:%s">%s</div></td></tr>' % (a, esc(head)))
        rows.append(
            '<tr><td style="padding:14px 28px;border-bottom:1px solid #e9ecf1">'
            '<a href="%s" style="font:700 18px/1.3 Georgia,serif;color:%s;text-decoration:none">%s</a>'
            '<div style="font:600 11px/1 -apple-system,Segoe UI,sans-serif;color:#8a93a3;margin:6px 0 8px;text-transform:uppercase;letter-spacing:.5px">%s</div>'
            '<div style="font:400 15px/1.55 -apple-system,Segoe UI,sans-serif;color:#3a4150">%s</div>'
            '<div style="font:400 13px/1.5 -apple-system,Segoe UI,sans-serif;margin-top:8px;padding:8px 12px;background:#f4f8f5;border-left:3px solid %s;border-radius:0 6px 6px 0;color:#2c5b3f"><b>Was es bedeutet:</b> %s</div>'
            '</td></tr>' % (esc(utm(it["link"])), dark, esc(it["title"]), esc(it["source"]),
                            esc(it.get("summary") or extractive_summary(it)), a, esc(it.get("meaning", "")))
        )
    pick_html = ""
    if pick:
        pick_html = ('<tr><td style="padding:18px 28px"><div style="background:%s;border-radius:12px;padding:18px 20px">'
                     '<div style="font:700 11px/1 -apple-system,Segoe UI,sans-serif;letter-spacing:2px;text-transform:uppercase;color:#bdf5d6">aban Pick · %s</div>'
                     '<a href="%s" style="display:block;font:700 17px/1.3 Georgia,serif;color:#fff;text-decoration:none;margin:8px 0 6px">%s</a>'
                     '<div style="font:400 13px/1.5 -apple-system,Segoe UI,sans-serif;color:#dff7e8">%s</div></div></td></tr>'
                     % (dark, esc(pick["label"]), esc(pick["link"]), esc(pick["title"]), esc(pick["why"])))
    ad_html = ""
    if ad:
        ad_html = ('<tr><td style="padding:8px 28px 14px"><div style="background:#fbf9f4;border:1px solid #ece3d3;border-radius:12px;padding:16px 18px">'
                   '<div style="font:700 10px -apple-system,Segoe UI,sans-serif;letter-spacing:1.5px;text-transform:uppercase;color:#b39a6b;margin-bottom:6px">%s</div>'
                   '<a href="%s" style="font:700 16px Georgia,serif;color:%s;text-decoration:none">%s</a>'
                   '<div style="font:400 14px/1.5 -apple-system,Segoe UI,sans-serif;color:#3a4150;margin:4px 0 8px">%s</div>'
                   '<a href="%s" style="display:inline-block;background:%s;color:#fff;font:700 13px -apple-system,Segoe UI,sans-serif;text-decoration:none;padding:9px 18px;border-radius:7px">%s</a>'
                   '</div></td></tr>' % (esc(ad.get("label", "Anzeige")), esc(ad["url"]), dark, esc(ad["name"]),
                                         esc(ad.get("blurb", "")), esc(ad["url"]), a, esc(ad.get("cta", "Mehr"))))
    cta_html = ""
    if cta:
        cta_html = ('<tr><td style="padding:18px 28px"><div style="border:2px solid %s;border-radius:12px;padding:18px 20px;text-align:center">'
                    '<div style="font:700 16px Georgia,serif;color:%s;margin-bottom:4px">%s</div>'
                    '<div style="font:400 13px/1.5 -apple-system,Segoe UI,sans-serif;color:#3a4150;margin-bottom:12px">%s</div>'
                    '<a href="%s" style="display:inline-block;background:%s;color:#fff;font:700 14px -apple-system,Segoe UI,sans-serif;text-decoration:none;padding:11px 22px;border-radius:8px">%s</a>'
                    '</div></td></tr>' % (a, dark, esc(cta["title"]), esc(cta.get("sub", "")), esc(cta["url"]), a, esc(cta["button"])))
    return (
        '<!doctype html><html lang="de"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>aban news — KI & Krypto Daily</title></head>'
        '<body style="margin:0;background:#eef1f5;padding:24px 0">'
        '<table role="presentation" width="100%%" cellpadding="0" cellspacing="0"><tr><td align="center">'
        '<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%%;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 8px 30px rgba(16,19,26,.08)">'
        '<tr><td style="background:%s;padding:24px 28px">'
        '<div style="font:800 22px/1 -apple-system,Segoe UI,sans-serif;color:#fff">aban<span style="color:%s">news</span></div>'
        '<div style="font:400 13px/1 -apple-system,Segoe UI,sans-serif;color:#aeb6c4;margin-top:6px">KI & Krypto · %s · in %d Minuten auf dem Laufenden</div>'
        '</td></tr>%s%s%s%s%s%s'
        '<tr><td style="padding:24px 28px;background:#fafbfc;text-align:center">'
        '<div style="font:400 13px/1.5 -apple-system,Segoe UI,sans-serif;color:#8a93a3">Taeglich kuratiert von <b>aban news</b>.</div>'
        '<a href="%s" style="display:inline-block;margin-top:12px;background:%s;color:#fff;font:700 14px -apple-system,Segoe UI,sans-serif;text-decoration:none;padding:11px 22px;border-radius:8px">Jetzt abonnieren</a>'
        '</td></tr></table></td></tr></table></body></html>'
    ) % (dark, a, _datestr(), mins, market_html, insight_html, pick_html, "".join(rows), ad_html, cta_html, utm(BRAND["url"], "footer"), a)


# ----------------------------------------------------------------------------- Feeds-Check
def check_feeds(topics):
    print("Quellen-Gesundheit:")
    ok = True
    for topic in topics:
        for name, url, _w in SOURCES[topic]:
            raw = fetch(url)
            n = len(parse_feed(raw, name, topic, 1)) if raw else 0
            status = "OK " if n else "LEER/FEHLER"
            if not n:
                ok = False
            print("  [%-3s] %-16s %3d  %s" % (topic, name, n, status))
    print("Engine-Extras:", "feedparser=%s" % bool(feedparser), "trafilatura=%s" % bool(trafilatura),
          "langdetect=%s" % bool(_lang_detect), "LLM=%s" % bool(os.environ.get("ANTHROPIC_API_KEY")))
    return 0 if ok else 1


# ----------------------------------------------------------------------------- Main
def main():
    ap = argparse.ArgumentParser(description="aban news Pro — KI/Krypto Daily-Digest-Generator")
    ap.add_argument("--topics", default="ki,krypto", help="Komma-Liste: ki,krypto (Default beide)")
    ap.add_argument("--max", type=int, default=8, help="max. Stories gesamt (Default 8)")
    ap.add_argument("--hours", type=int, default=30, help="nur Artikel der letzten N Stunden (Default 30)")
    ap.add_argument("--out", default="out", help="Zielordner (Default out/)")
    ap.add_argument("--currency", default="chf", help="Markt-Snapshot-Waehrung (Default chf)")
    ap.add_argument("--no-fulltext", action="store_true", help="Volltext-Holen (trafilatura) aus")
    ap.add_argument("--no-llm", action="store_true", help="LLM-Veredelung aus (auch wenn Key gesetzt)")
    ap.add_argument("--no-market", action="store_true", help="Markt-Snapshot aus")
    ap.add_argument("--check-feeds", action="store_true", help="nur Quellen pruefen, nichts bauen")
    ap.add_argument("--edition", default="pro", choices=["pro", "free", "both"],
                    help="pro=voller Digest (Default), free=Teaser Top-N + Pro-CTA, both=beide")
    ap.add_argument("--free-count", type=int, default=5, help="Stories in der Free-Edition (Default 5)")
    ap.add_argument("--partners", default=os.path.join(HERE_DIR, "partners.json"),
                    help="Affiliate-/Partner-JSON (Default partners.json; fehlt = keine Anzeige)")
    ap.add_argument("--no-ads", action="store_true", help="Anzeigen-/Affiliate-Block aus")
    ap.add_argument("--model", default=os.environ.get("ABAN_LLM_MODEL", "claude-haiku-4-5-20251001"),
                    help="LLM-Modell fuer die Veredelung (ENV ABAN_LLM_MODEL)")
    args = ap.parse_args()

    topics = [t.strip() for t in args.topics.split(",") if t.strip() in SOURCES]
    if not topics:
        print("Keine gueltigen Topics. Erlaubt: ki, krypto", file=sys.stderr)
        return 2
    if args.check_feeds:
        return check_feeds(topics)

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=args.hours)
    print("aban news Pro — sammle %s (letzte %dh) …" % ("+".join(topics), args.hours))

    raw_items = []
    for topic in topics:
        for name, url, weight in SOURCES[topic]:
            got = parse_feed(fetch(url), name, topic, weight)
            print("  · %-16s %2d Artikel" % (name, len(got)))
            raw_items += got

    fresh = [it for it in raw_items if (it["published"] is None) or (it["published"] >= cutoff)]
    fresh = dedupe(fresh)
    fresh.sort(key=lambda it: score(it, now), reverse=True)

    # ausgewogen je Topic, dann nach Score auffuellen
    selected, per, quota = [], {}, max(1, args.max // max(1, len(topics)))
    for it in fresh:
        if per.get(it["topic"], 0) < quota:
            selected.append(it); per[it["topic"]] = per.get(it["topic"], 0) + 1
    for it in fresh:
        if len(selected) >= args.max:
            break
        if it not in selected:
            selected.append(it)
    selected = selected[:args.max]
    if not selected:
        print("Keine frischen Artikel — --hours erhoehen oder Quellen pruefen (--check-feeds).", file=sys.stderr)
        return 1

    if not args.no_fulltext:
        print("  … Volltext der Top-%d Artikel holen%s" % (len(selected), "" if trafilatura else " (trafilatura fehlt → Feed-Snippet)"))
        enrich_fulltext(selected)

    ranked = sorted(selected, key=lambda it: -score(it, now))
    selected.sort(key=lambda it: (0 if it["topic"] == "ki" else 1, -score(it, now)))

    market = None if args.no_market else market_snapshot(args.currency)

    used_llm, insight = (False, None)
    if not args.no_llm:
        used_llm, insight = llm_enhance(selected, args.model)
    used = {}
    for it in selected:
        it.setdefault("summary", extractive_summary(it))
        if not it.get("meaning"):
            it["meaning"] = heuristic_meaning(it, used)
        it["lang"] = detect_lang(it)
    if not insight:
        insight = heuristic_insight(selected, market)
    pick = pick_of_day(ranked, used)
    mins = reading_time(selected)

    os.makedirs(args.out, exist_ok=True)
    stamp = now.astimezone().strftime("%Y-%m-%d")
    pro_url = os.environ.get("ABAN_PRO_URL", "https://abannews.com/pro")

    ad = None
    if not args.no_ads:
        partners = load_partners(args.partners)
        lead_topic = ranked[0]["topic"] if ranked else "ki"
        ad = pick_partner(partners, lead_topic, now.timetuple().tm_yday)
        if ad:
            print("  Anzeige: %s (%s)" % (ad["name"], ad.get("topic", "any")))

    def write_edition(its, suffix, cta):
        base = os.path.join(args.out, "aban-%s%s" % (stamp, suffix))
        open(base + ".html", "w", encoding="utf-8").write(render_html(its, pick, insight, market, mins, cta, ad))
        open(base + ".md", "w", encoding="utf-8").write(render_md(its, pick, insight, market, mins, cta, ad))
        open(base + ".txt", "w", encoding="utf-8").write(render_txt(its, pick, insight, market, mins, cta, ad))
        json.dump({"date": stamp, "edition": "free" if suffix else "pro", "generated": now.isoformat(),
                   "llm": used_llm, "minutes": mins, "insight": insight, "market": market, "pick": pick,
                   "items": [{k: (v.isoformat() if isinstance(v, datetime) else v)
                              for k, v in it.items() if not k.startswith("_")} for it in its]},
                  open(base + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        return base

    written = []
    if args.edition in ("pro", "both"):
        written.append(write_edition(selected, "", None))
    if args.edition in ("free", "both"):
        # Teaser: Top-N, gekuerzte Summaries, CTA zur Pro-Edition (Stripe-Payment-Link via ABAN_PRO_URL)
        free_items = []
        for it in selected[:max(1, args.free_count)]:
            c = dict(it); c["summary"] = first_sentences(it.get("summary") or "", 1, 130); free_items.append(c)
        hidden = len(selected) - len(free_items)
        cta = {"title": "Mehr im aban Pro-Digest",
               "sub": ("Heute %d weitere Stories, volle Einordnung, Markt-Tiefe & Archiv." % hidden) if hidden > 0
                      else "Volle Einordnung, Markt-Tiefe & Archiv — werde aban Pro.",
               "button": "aban Pro werden", "url": utm(pro_url, "cta")}
        written.append(write_edition(free_items, "-free", cta))

    print("\n✓ %d Stories · %d Min · LLM:%s · Volltext:%s · Markt:%s · Edition:%s" % (
        len(selected), mins, "an" if used_llm else "aus", "an" if (trafilatura and not args.no_fulltext) else "aus",
        "an" if market else "aus", args.edition))
    for b in written:
        print("  %s.html / .md / .txt / .json" % b)
    print("  Insight: %s" % insight)
    if pick:
        print("  aban Pick: %s" % pick["title"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
