#!/usr/bin/env python3
"""
aban news Pro — Onboarding-Mails (Double-Opt-in + Welcome).

Baut zwei gebrandete E-Mail-Templates fuer den Anmelde-Flow:

    out/email-confirm.html   Double-Opt-in: "Bitte bestaetige deine Anmeldung" (DSGVO)
    out/email-welcome.html   Begruessung nach Bestaetigung (+ Erwartung + erster Wert)

Platzhalter, die der Versender / Cloudflare-Worker je Empfaenger ersetzt:
    {{EMAIL}}        E-Mail-Adresse
    {{CONFIRM_URL}}  Bestaetigungs-Link (Worker /confirm?e=..&t=..)
    {{UNSUB_URL}}    Abmelde-Link

Auch direkt nutzbar zum Rendern einer konkreten Mail (mit Token):
    python aban_welcome.py --email du@example.com   # gibt fertige Confirm-Mail aus

ENV: UNSUB_SECRET (Token), CONFIRM_BASE (Default https://abannews.com/confirm),
     UNSUB_URL (Default https://abannews.com/abmelden), ABAN_PRO_URL.
"""
import os, sys, html, hmac, hashlib, argparse, urllib.parse

ACCENT, DARK, CREAM, URL = "#0b5", "#10131a", "#faf7f2", "https://abannews.com"


def token(email, purpose="confirm"):
    secret = os.environ.get("UNSUB_SECRET", "CHANGE_ME").encode()
    return hmac.new(secret, ("%s:%s" % (purpose, email.lower())).encode(), hashlib.sha256).hexdigest()[:24]


def confirm_url(email):
    base = os.environ.get("CONFIRM_BASE", "https://abannews.com/confirm")
    q = urllib.parse.urlencode({"e": email, "t": token(email, "confirm")})
    return base + ("&" if "?" in base else "?") + q


def unsub_url(email):
    base = os.environ.get("UNSUB_URL", "https://abannews.com/abmelden")
    q = urllib.parse.urlencode({"e": email, "t": token(email, "unsub")})
    return base + ("&" if "?" in base else "?") + q


def _shell(inner):
    return (
        '<!doctype html><html lang="de"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"></head>'
        '<body style="margin:0;background:#eef1f5;padding:24px 0;font-family:-apple-system,Segoe UI,sans-serif">'
        '<table role="presentation" width="100%%" cellpadding="0" cellspacing="0"><tr><td align="center">'
        '<table role="presentation" width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%%;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 8px 30px rgba(16,19,26,.08)">'
        '<tr><td style="background:%s;padding:24px 28px">'
        '<div style="font:800 22px -apple-system,Segoe UI,sans-serif;color:#fff">aban<span style="color:%s">news</span></div>'
        '</td></tr>%s</table></td></tr></table></body></html>'
    ) % (DARK, ACCENT, inner)


def confirm_template():
    inner = (
        '<tr><td style="padding:28px">'
        '<h1 style="font:700 24px Georgia,serif;color:#10131a;margin:0 0 10px">Fast geschafft — bitte bestaetigen</h1>'
        '<p style="font:400 15px/1.6 -apple-system,Segoe UI,sans-serif;color:#3a4150;margin:0 0 18px">'
        'Du hast dich fuer <b>aban news</b> angemeldet — taeglich KI &amp; Krypto in 5 Minuten, auf Deutsch. '
        'Klicke kurz zur Bestaetigung (Double-Opt-in, DSGVO):</p>'
        '<p style="text-align:center;margin:0 0 18px"><a href="{{CONFIRM_URL}}" '
        'style="display:inline-block;background:%s;color:#fff;font:700 15px -apple-system,Segoe UI,sans-serif;'
        'text-decoration:none;padding:14px 28px;border-radius:8px">Anmeldung bestaetigen</a></p>'
        '<p style="font:400 13px/1.5 -apple-system,Segoe UI,sans-serif;color:#8a93a3;margin:0">'
        'Falls der Button nicht geht: {{CONFIRM_URL}}<br>'
        'Du hast das nicht angefordert? Ignoriere diese Mail einfach.</p>'
        '</td></tr>' % ACCENT
    )
    return _shell(inner)


def welcome_template():
    pro = os.environ.get("ABAN_PRO_URL", "https://abannews.com/pro")
    inner = (
        '<tr><td style="padding:28px">'
        '<h1 style="font:700 24px Georgia,serif;color:#10131a;margin:0 0 10px">Willkommen bei aban news</h1>'
        '<p style="font:400 15px/1.6 -apple-system,Segoe UI,sans-serif;color:#3a4150;margin:0 0 16px">'
        'Schoen, dass du dabei bist. Ab jetzt bekommst du jeden Morgen die wichtigsten '
        '<b>KI- &amp; Krypto-News</b> kompakt auf Deutsch — mit Markt-Snapshot, Einordnung und einem taeglichen Pick.</p>'
        '<div style="background:%s;border-radius:12px;padding:16px 18px;margin:0 0 16px">'
        '<div style="font:700 13px -apple-system,Segoe UI,sans-serif;color:#8b7355;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px">Was dich erwartet</div>'
        '<ul style="margin:0;padding-left:18px;font:400 14px/1.7 -apple-system,Segoe UI,sans-serif;color:#3a4150">'
        '<li>Taeglich um 7 Uhr: KI + Krypto in 5 Minuten</li>'
        '<li>BTC/ETH-Markt-Snapshot &amp; "Was es bedeutet" pro Story</li>'
        '<li>Sonntags: der aban Pro Deep-Dive (Tiefenanalyse der Woche)</li></ul></div>'
        '<p style="text-align:center;margin:0 0 16px"><a href="%s" '
        'style="display:inline-block;background:%s;color:#fff;font:700 14px -apple-system,Segoe UI,sans-serif;'
        'text-decoration:none;padding:12px 24px;border-radius:8px">aban Pro entdecken</a></p>'
        '<p style="font:400 12px/1.5 -apple-system,Segoe UI,sans-serif;color:#9aa3b2;margin:0">'
        'Du erhaeltst diese Mails als aban-news-Abonnent. <a href="{{UNSUB_URL}}" style="color:#9aa3b2">Abmelden</a>.</p>'
        '</td></tr>' % (CREAM, E_utm(pro), ACCENT)
    )
    return _shell(inner)


def E_utm(link):
    sep = "&" if "?" in link else "?"
    return link + sep + urllib.parse.urlencode({"utm_source": "abannews", "utm_medium": "welcome"})


def fill(tpl, email):
    return (tpl.replace("{{EMAIL}}", html.escape(email))
               .replace("{{CONFIRM_URL}}", html.escape(confirm_url(email)))
               .replace("{{UNSUB_URL}}", html.escape(unsub_url(email))))


def main():
    ap = argparse.ArgumentParser(description="aban news Pro — Onboarding-Mails")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
    ap.add_argument("--email", help="konkrete Confirm-Mail mit Token fuer diese Adresse rendern")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    if args.email:
        sys.stdout.write(fill(confirm_template(), args.email))
        return 0

    open(os.path.join(args.out, "email-confirm.html"), "w", encoding="utf-8").write(confirm_template())
    open(os.path.join(args.out, "email-welcome.html"), "w", encoding="utf-8").write(welcome_template())
    print("✓ Templates: out/email-confirm.html, out/email-welcome.html")
    print("  Platzhalter {{CONFIRM_URL}}/{{UNSUB_URL}} ersetzt der Worker/Versender je Empfaenger.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
