#!/usr/bin/env python3
"""
aban news Pro — Versand-Tool (SMTP, provider-agnostisch).

Nimmt die von aban_news_pro.py erzeugte Ausgabe (HTML + Plaintext) und verschickt sie
an eine Abonnentenliste. Reine Standardbibliothek (smtplib, email).

  • Dry-Run ist Default → zeigt Empfaenger + Vorschau, sendet NICHTS. Erst --send sendet wirklich.
  • multipart/alternative: Plaintext (.txt) + HTML (.html) — beste Zustellbarkeit.
  • Pflicht-Compliance: List-Unsubscribe-Header + sichtbarer Abmelde-Link je Empfaenger
    (Token = HMAC aus E-Mail + UNSUB_SECRET, faelschungssicher).
  • Editionen: free | pro | both  (Spalte 'edition' in der Liste; 'both' = alle Aktiven).
  • Batch + Pause gegen Provider-Ratenlimits.

ENV (NIE im Code/Git — als Secret/ENV setzen):
    SMTP_HOST   z.B. smtp-relay.brevo.com / smtp.mailjet.com / smtp.gmail.com
    SMTP_PORT   587 (STARTTLS, Default) oder 465 (SSL)
    SMTP_USER   SMTP-Login
    SMTP_PASS   SMTP-Passwort / API-Key
    MAIL_FROM   Absender-Adresse (z.B. news@abannews.com)   [Pflicht zum Senden]
    MAIL_FROM_NAME  Anzeigename (Default "aban news")
    UNSUB_SECRET    Geheimnis fuer den Abmelde-Token (Default = unsicher, bitte setzen)
    UNSUB_URL       Basis-URL der Abmelde-Seite (Default https://abannews.com/abmelden)

Abonnentenliste (CSV, Header: email,edition,status,joined):
    --list content/aban/subscribers.csv   (Default; echte Liste ist .gitignore't)
    subscribers.sample.csv liegt als Vorlage bei. Status 'active' wird gesendet.

Nutzung:
    python aban_send.py                          # Dry-Run, neueste Ausgabe, alle Aktiven
    python aban_send.py --edition pro            # nur Pro-Abonnenten (Dry-Run)
    python aban_send.py --file out/aban-2026-06-11.html
    python aban_send.py --send                   # WIRKLICH senden (SMTP-ENV noetig)
    python aban_send.py --send --test you@x.de   # Test: nur an EINE Adresse senden
"""
import os, re, csv, sys, ssl, glob, time, json, hmac, hashlib, smtplib, argparse, urllib.parse
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import formataddr, make_msgid

HERE = os.path.dirname(os.path.abspath(__file__))


def newest(pattern):
    files = sorted(glob.glob(os.path.join(HERE, pattern)))
    return files[-1] if files else None


def load_issue(html_path):
    """Laedt HTML + (gleichnamige) .txt + .json-Metadaten."""
    base = re.sub(r"\.html$", "", html_path)
    html = open(html_path, encoding="utf-8").read()
    txt = ""
    if os.path.exists(base + ".txt"):
        txt = open(base + ".txt", encoding="utf-8").read()
    meta = {}
    if os.path.exists(base + ".json"):
        try:
            meta = json.load(open(base + ".json", encoding="utf-8"))
        except Exception:
            pass
    return html, txt, meta


def subject_for(meta):
    d = meta.get("date") or datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")
    try:
        d = datetime.strptime(d, "%Y-%m-%d").strftime("%d.%m.%Y")
    except Exception:
        pass
    insight = (meta.get("insight") or "").strip()
    # kurzer, neugierig machender Betreff aus dem Insight, sonst Standard
    if insight:
        lead = re.split(r"(?<=[.!?])\s", insight)[0]
        if 8 <= len(lead) <= 70:
            return "aban news · %s — %s" % (d, lead)
    return "aban news · KI & Krypto — %s" % d


def load_subscribers(path, edition):
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            email = (r.get("email") or "").strip().lower()
            if not email or "@" not in email:
                continue
            status = (r.get("status") or "active").strip().lower()
            ed = (r.get("edition") or "free").strip().lower()
            if status != "active":
                continue
            if edition != "both" and ed != edition:
                continue
            rows.append({"email": email, "edition": ed, "joined": r.get("joined", "")})
    # Duplikate raus
    seen, out = set(), []
    for r in rows:
        if r["email"] not in seen:
            seen.add(r["email"]); out.append(r)
    return out


def unsub_token(email):
    # Schema MUSS zum Cloudflare-Worker + aban_welcome.py passen: HMAC("unsub:"+email), 24 hex.
    secret = os.environ.get("UNSUB_SECRET", "CHANGE_ME").encode()
    return hmac.new(secret, ("unsub:" + email.lower()).encode(), hashlib.sha256).hexdigest()[:24]


def unsub_link(email):
    base = os.environ.get("UNSUB_URL", "https://abannews.com/abmelden")
    q = urllib.parse.urlencode({"e": email, "t": unsub_token(email)})
    return base + ("&" if "?" in base else "?") + q


def personalize(html, txt, email):
    """Fuegt je Empfaenger einen Abmelde-Link ein (Platzhalter {{UNSUB}} oder Footer-Anhang)."""
    link = unsub_link(email)
    if "{{UNSUB}}" in html:
        html = html.replace("{{UNSUB}}", link)
    else:
        foot = ('<div style="text-align:center;font:400 11px -apple-system,Segoe UI,sans-serif;'
                'color:#9aa3b2;padding:10px 28px 20px">Du erhaeltst diese Mail als aban-news-Abonnent. '
                '<a href="%s" style="color:#9aa3b2">Abmelden</a></div>' % link)
        html = re.sub(r"</body>", foot + "</body>", html, count=1) if "</body>" in html else html + foot
    txt = (txt or "") + "\n\nAbmelden: " + link
    return html, txt


def build_message(from_addr, from_name, to_addr, subject, html, txt):
    msg = EmailMessage()
    msg["From"] = formataddr((from_name, from_addr))
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg["Message-ID"] = make_msgid(domain=from_addr.split("@")[-1])
    # Pflicht fuer seriose Newsletter:
    msg["List-Unsubscribe"] = "<%s>" % unsub_link(to_addr)
    msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    msg.set_content(txt or "Bitte HTML-Ansicht aktivieren.")
    msg.add_alternative(html, subtype="html")
    return msg


def smtp_connect():
    host = os.environ.get("SMTP_HOST"); port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER"); pw = os.environ.get("SMTP_PASS")
    if not (host and user and pw):
        raise RuntimeError("SMTP_HOST/SMTP_USER/SMTP_PASS fehlen (als ENV/Secret setzen).")
    ctx = ssl.create_default_context()
    if port == 465:
        s = smtplib.SMTP_SSL(host, port, context=ctx, timeout=30)
    else:
        s = smtplib.SMTP(host, port, timeout=30); s.ehlo(); s.starttls(context=ctx); s.ehlo()
    s.login(user, pw)
    return s


def main():
    ap = argparse.ArgumentParser(description="aban news Pro — Newsletter-Versand (SMTP)")
    ap.add_argument("--file", help="HTML-Ausgabe (Default: neueste out/aban-*.html)")
    ap.add_argument("--list", default=os.path.join(HERE, "subscribers.csv"), help="Abonnenten-CSV")
    ap.add_argument("--edition", default="both", choices=["free", "pro", "both"], help="Zielgruppe")
    ap.add_argument("--send", action="store_true", help="WIRKLICH senden (sonst Dry-Run)")
    ap.add_argument("--test", help="Test: nur an diese eine Adresse senden")
    ap.add_argument("--batch", type=int, default=40, help="Mails pro Batch (Default 40)")
    ap.add_argument("--pause", type=float, default=2.0, help="Sekunden Pause zwischen Batches")
    ap.add_argument("--subject", help="Betreff ueberschreiben")
    args = ap.parse_args()

    html_path = args.file or newest("out/aban-*.html")
    if not html_path or not os.path.exists(html_path):
        print("Keine Newsletter-Ausgabe gefunden — erst aban_news_pro.py laufen lassen.", file=sys.stderr)
        return 1
    html, txt, meta = load_issue(html_path)
    subject = args.subject or subject_for(meta)
    from_addr = os.environ.get("MAIL_FROM")
    from_name = os.environ.get("MAIL_FROM_NAME", "aban news")

    if args.test:
        recipients = [{"email": args.test.strip().lower(), "edition": "test", "joined": ""}]
    else:
        recipients = load_subscribers(args.list, args.edition)

    print("Ausgabe : %s" % os.path.basename(html_path))
    print("Betreff : %s" % subject)
    print("Edition : %s" % args.edition)
    print("Liste   : %s" % (args.test or args.list))
    print("Empfaenger: %d" % len(recipients))
    if meta.get("market", {}):
        m = meta["market"]; print("Markt   : BTC %s | ETH %s" % (m.get("btc_str", "?"), m.get("eth_str", "?")))

    if not recipients:
        print("\nKeine aktiven Empfaenger fuer diese Edition. (Liste pruefen / subscribers.sample.csv kopieren.)")
        return 0

    if not args.send:
        print("\n[DRY-RUN] Es wird NICHTS gesendet. Zum echten Versand: --send (SMTP-ENV noetig).")
        print("Beispiel-Empfaenger:", ", ".join(r["email"] for r in recipients[:5]),
              ("… +%d" % (len(recipients) - 5)) if len(recipients) > 5 else "")
        print("Abmelde-Link (Beispiel):", unsub_link(recipients[0]["email"]))
        return 0

    if not from_addr:
        print("MAIL_FROM fehlt — Absenderadresse als ENV setzen.", file=sys.stderr)
        return 2

    print("\n>>> SENDE wirklich …")
    try:
        s = smtp_connect()
    except Exception as e:
        print("SMTP-Verbindung fehlgeschlagen: %s" % e, file=sys.stderr)
        return 2
    sent, failed = 0, 0
    try:
        for i, r in enumerate(recipients, 1):
            h, t = personalize(html, txt, r["email"])
            msg = build_message(from_addr, from_name, r["email"], subject, h, t)
            try:
                s.send_message(msg); sent += 1
            except Exception as e:
                failed += 1; print("  ! %s: %s" % (r["email"], e), file=sys.stderr)
            if i % args.batch == 0 and i < len(recipients):
                time.sleep(args.pause)
                try:
                    s.noop()
                except Exception:
                    s = smtp_connect()
    finally:
        try:
            s.quit()
        except Exception:
            pass
    print("\n✓ gesendet: %d  | fehlgeschlagen: %d" % (sent, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
