# 📰 aban news Pro — KI/Krypto-Newsletter-System

Eigenständiges, portierbares Toolset für den täglichen DACH-Newsletter **aban news**
(`abannews.com`). Holt KI- & Krypto-News, baut eine versandfertige Ausgabe, verschickt
sie und pflegt ein öffentliches Archiv. **Reine Standardbibliothek** + optionale Extras
(läuft auch ohne). Keine Secrets im Code — alles über ENV.

## Bausteine

| Tool | Zweck |
|---|---|
| `aban_news_pro.py` | **Engine:** Feeds → Digest (HTML/MD/TXT/JSON), Markt-Snapshot, Insight, Pick, Editionen |
| `aban_send.py` | **Versand:** SMTP, multipart, List-Unsubscribe, Editionen, Dry-Run-Default |
| `aban_deepdive.py` | **Wochen-Deep-Dive (Pro-exklusiv):** Thema der Woche + Langanalyse aus den 7-Tage-Ausgaben |
| `aban_archive.py` | **Archiv:** Übersichtsseite (`out/index.html`) aus allen Ausgaben = SEO-Motor |
| `.github/workflows/aban-news.yml` | **Automation:** täglich 07:00 CH bauen + (optional) versenden + sonntags Deep-Dive + Archiv committen |

## Schnellstart

```bash
# Extras (optional, empfohlen) — Debian/Ubuntu-Workaround:
SETUPTOOLS_USE_DISTUTILS=stdlib pip install -r requirements.txt

cd content/aban
python aban_news_pro.py --check-feeds          # Quellen-Gesundheit
python aban_news_pro.py --edition both          # Pro + Free bauen -> out/
python aban_archive.py                          # Archiv-Index bauen
python aban_send.py --list subscribers.sample.csv   # Dry-Run (sendet nichts)
```

## Engine (`aban_news_pro.py`)

Macht automatisch: 12 kuratierte DACH-Feeds (KI+Krypto) ziehen → dedupe → ranken →
**Volltext** der Top-Artikel holen → deutsch zusammenfassen → **Markt-Snapshot** (BTC/ETH
live) → **aban Insight** (Tages-Synthese) → **aban Pick** → pro Story **„Was es bedeutet"**.

```
--topics ki,krypto     Themen (Default beide)
--max 8                Stories gesamt
--hours 30             Zeitfenster
--edition pro|free|both  pro=voll, free=Teaser Top-N + Pro-CTA
--free-count 5         Stories in der Free-Edition
--currency chf         Markt-Snapshot-Währung
--no-fulltext / --no-llm / --no-market   Stufen abschalten
--check-feeds          nur Quellen prüfen
```

**Was es einzigartig macht:** deutscher DACH-Fokus, KI **und** Krypto in einer 5-Min-Mail,
Markt-Snapshot + handlungsorientierte Einordnung pro Story + Tages-Insight — so gebündelt
gibt es das sonst nicht.

### ENV
| Variable | Wirkung |
|---|---|
| `ANTHROPIC_API_KEY` | LLM-Veredelung: unique DE-Summary + Einordnung + Insight (sonst Heuristik) |
| `ABAN_LLM_MODEL` | Modell-Override (Default: schnelles, günstiges Claude-Modell) |
| `ABAN_PRO_URL` | Ziel des Free-Editions-CTA (Stripe-Payment-Link) |

## Versand (`aban_send.py`)

Verschickt die generierte Ausgabe per SMTP (provider-agnostisch). **Dry-Run ist Default.**

```
python aban_send.py                         # Dry-Run, neueste Ausgabe
python aban_send.py --edition pro           # nur Pro-Liste (Dry-Run)
python aban_send.py --send --test you@x.de  # echter Test an EINE Adresse
python aban_send.py --send                  # echter Versand an alle Aktiven
```

| ENV | Wert |
|---|---|
| `SMTP_HOST/PORT/USER/PASS` | z.B. Brevo/Mailjet/Gmail (Port 587 STARTTLS oder 465 SSL) |
| `MAIL_FROM` / `MAIL_FROM_NAME` | Absender (z.B. `news@abannews.com`) |
| `UNSUB_SECRET` | Geheimnis für faelschungssichere Abmelde-Tokens |
| `UNSUB_URL` | Basis-URL der Abmelde-Seite (Default `https://abannews.com/abmelden`) |

Abonnenten-CSV (`subscribers.csv`, **.gitignore't**), Header `email,edition,status,joined`.
Vorlage: `subscribers.sample.csv`. Pflicht: `List-Unsubscribe` + One-Click + sichtbarer Link.

## Wochen-Deep-Dive (`aban_deepdive.py`) — stärkstes Pro-Argument

```bash
python aban_deepdive.py            # letzte 7 Tage, Thema der Woche, Langanalyse
python aban_deepdive.py --topic ki # nur KI
```
Liest die 7-Tage-Ausgaben, erkennt das **Thema der Woche** und schreibt einen strukturierten
deutschen Deep-Dive (mit `ANTHROPIC_API_KEY` LLM-veredelt, sonst Fallback). Pro-exklusiv —
das wiederkehrende Argument, Pro zu abonnieren. ENV `ABAN_DEEPDIVE_MODEL` (Default starkes Claude-Modell).
Im Workflow läuft er automatisch **sonntags**.

## Monetarisierung (Pro-Tier, ohne Backend)

1. **Free-Edition** (`--edition free`) = Top-5-Teaser + CTA „aban Pro werden" (`ABAN_PRO_URL`).
2. **Stripe Payment Link** anlegen (kein Server nötig): Stripe → Produkt „aban Pro" → Payment Link → URL als `ABAN_PRO_URL`.
3. **Pro-Liste pflegen:** zahlende Kund:innen aus dem Stripe-Export in `subscribers.csv` mit `edition=pro` übernehmen.
4. Workflow versendet Free an Free-Liste und Pro an Pro-Liste.

Wert für Pro: voller Digest (alle Stories), Markt-Tiefe, wöchentlicher Deep-Dive, Archiv.

## Anmeldung & Onboarding (Double-Opt-in, serverlos)

Drei Teile, die zusammenspielen — kein eigener Server nötig (Cloudflare):

1. **`signup-widget.html`** — Drop-in-Formular fürs Landing. POSTet die E-Mail an `data-endpoint`.
2. **`aban-cloudflare-worker.js`** — das Backend: `/subscribe` (speichert + sendet Bestätigung),
   `/confirm` (Double-Opt-in + Welcome-Mail), `/abmelden`, `/export` (CSV der Aktiven für `aban_send.py`).
   KV-Namespace `ABAN_SUBS`; ENV `UNSUB_SECRET` (gleich wie in den Python-Tools), `RESEND_API_KEY`/`MAIL_FROM`, `ADMIN_KEY`.
3. **`aban_welcome.py`** — gebrandete Confirm-/Welcome-Mail-Templates (`out/email-confirm.html`, `out/email-welcome.html`)
   mit Platzhaltern `{{CONFIRM_URL}}`/`{{UNSUB_URL}}`. `--email du@x.de` rendert eine konkrete Mail mit Token.

**Token-Schema ist überall identisch** (`HMAC(UNSUB_SECRET, "<purpose>:<email>")`, 24 hex) → Abmelde-/Confirm-Links
aus Worker, `aban_send.py` und `aban_welcome.py` sind gegenseitig gültig. Setze `UNSUB_SECRET` einmal gleich.

Ablauf: Widget → Worker `/subscribe` → Bestätigungsmail → Klick `/confirm` → aktiv + Welcome-Mail.
Liste per `/export?key=ADMIN_KEY` als CSV ziehen → `aban_send.py --list`.

## Referral-Wachstums-Loop (Morning-Brew-Mechanik)

Eingebaut im Worker — jeder bestätigte Abonnent bekommt `abannews.com/?ref=CODE`. Wer andere wirbt,
schaltet **Pro gratis** frei: **3** Werbungen → 1 Monat · **10** → 3 Monate · **25** → 12 Monate.

- Widget/Landing senden `?ref=` automatisch mit (`/subscribe`).
- Bei `/confirm` wird dem Werber die Empfehlung gutgeschrieben + bei Meilenstein Pro aktiviert (+ Glückwunsch-Mail).
- `/status?e=&t=` zeigt Stand, Share-Link und nächsten Meilenstein. Welcome-Mail enthält Link + Status.
- `/export` markiert Werber mit aktivem `pro_until` als `pro` → `aban_send.py` sendet ihnen die Pro-Edition.

Selbstverstärkend: mehr Abonnenten → mehr Werber → mehr Abonnenten. Kostet nichts (Pro ist digital).

## Wachstum / Analytics

- **UTM-Tags** auf allen Links (`utm_source=abannews…`) → Klicks über die Site-Analytik (Cloudflare/GA), ohne Infra.
- **Archiv** (`aban_archive.py` → `out/index.html`) als `/archiv/` veröffentlichen → Google-Traffic → neue Abonnenten.

## Automation (`.github/workflows/aban-news.yml`)

Täglich 05:00 UTC (07:00 CH) oder manuell („Run workflow"). Baut Pro+Free, aktualisiert das
Archiv, committet die Ausgabe; **versendet nur**, wenn SMTP-Secrets gesetzt sind **und** der
Dispatch-Input `send=true` ist. Cron greift **erst auf `main`** (geplante Workflows nur auf Default-Branch).
Optional: ganze Abonnentenliste als Secret `ABAN_SUBSCRIBERS` (CSV-Inhalt) bereitstellen.

## ⚠️ Bleibt User-Hand (nicht committbar)
- Secrets setzen: `ANTHROPIC_API_KEY`, SMTP-Zugang, `UNSUB_SECRET`, `ABAN_PRO_URL`, ggf. `ABAN_SUBSCRIBERS`.
- Stripe-Konto + Payment Link; zahlende Kund:innen in die Pro-Liste übernehmen.
- Tools ins private Repo `aban-news-landing` kopieren bzw. dort den Signup an die Liste anbinden.
- Mails real versenden / Zahlungen verarbeiten (gated auf Secrets).

## Abhängigkeiten
`requirements.txt` (alle optional): `feedparser`, `trafilatura`, `langdetect`. Ohne sie greift
ein stdlib-Fallback (eigener XML-Parser, Feed-Snippet statt Volltext).
