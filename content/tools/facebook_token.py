#!/usr/bin/env python3
"""
LuxeStyle Facebook **Page-Token-Helfer** — holt ein langlebiges, **nie ablaufendes**
Page-Token in einem Rutsch und prüft es. Ersetzt die 3 manuellen curl-Schritte, die
erfahrungsgemäß oft schiefgehen.

Trick: Ein Page-Token, das aus einem **langlebigen User-Token** gezogen wird, läuft NICHT ab
(solange App + Berechtigungen bestehen).

Ablauf (macht das Skript automatisch):
  1) kurzlebiges User-Token  --(fb_exchange_token)-->  langlebiges User-Token (60 Tage)
  2) langlebiges User-Token  --(/me/accounts)-->        Page-Token der Seite (läuft NICHT ab)
  3) /debug_token            --(Prüfung)-->             Type=PAGE, Expires=Never

Vorbereitung (einmalig, im Graph API Explorer):
  - App „LuxeStyle Social" wählen → „Generate Access Token"
  - Scopes anhaken: pages_show_list, pages_read_engagement, pages_manage_posts,
    pages_manage_engagement, instagram_basic, instagram_content_publish
  - Das erzeugte (kurzlebige) USER-Token kopieren — das gibst du hier ein.

ENV (lokal, nie committen):
  FB_APP_ID       deine App-ID
  FB_APP_SECRET   dein App-Geheimcode (NICHT als Token verwenden!)
  FB_PAGE_ID      optional, Default = LuxeStyle CH 1049840534888592

Nutzung (Token NIE als Argument — landet sonst in der Shell-History):
  FB_APP_ID=... FB_APP_SECRET=... python facebook_token.py
  (fragt das kurzlebige User-Token interaktiv ab; oder via  FB_SHORT_TOKEN=...  env / stdin-Pipe)

Ausgabe: das fertige Page-Token + Prüfergebnis. Danach als GitHub-Secret setzen:
  FB_PAGE_ACCESS_TOKEN = <Page-Token>   (und optional META_ACCESS_TOKEN = dasselbe)

Nur Standardbibliothek (urllib).
"""
import os, sys, re, json, getpass, urllib.parse, urllib.request, urllib.error

GRAPH = "https://graph.facebook.com/v21.0"
DEFAULT_PAGE = "1049840534888592"   # LuxeStyle CH


def _get(path, params):
    url = GRAPH + path + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.loads(r.read()), None
    except urllib.error.HTTPError as e:
        return None, e.read().decode()[:700]


def fail(msg):
    sys.exit("✗ " + msg)


def main():
    app_id = os.environ.get("FB_APP_ID")
    app_secret = os.environ.get("FB_APP_SECRET")
    if not (app_id and app_secret):
        fail("Bitte ENV setzen: FB_APP_ID + FB_APP_SECRET (App → Einstellungen → Basic).")
    page_id = os.environ.get("FB_PAGE_ID", DEFAULT_PAGE)

    # kurzlebiges User-Token einlesen (env / stdin-Pipe / interaktive, nicht-echoende Abfrage)
    short = os.environ.get("FB_SHORT_TOKEN", "").strip()
    if not short and not sys.stdin.isatty():
        short = sys.stdin.read().strip()
    if not short:
        short = getpass.getpass("Kurzlebiges USER-Token (aus Graph API Explorer) einfügen: ").strip()
    if not short:
        fail("Kein Token eingegeben.")

    # Stolperfalle #1: App-Secret statt Token
    if short == app_secret or re.fullmatch(r"[0-9a-fA-F]{32}", short):
        fail("Das sieht aus wie dein **App-Secret** (32 Hex-Zeichen), nicht wie ein Access-Token.\n"
             "  Ein echtes Token ist lang (100+ Zeichen) und beginnt meist mit 'EAA…'.\n"
             "  Im Graph API Explorer auf 'Generate Access Token' klicken und DEN Wert kopieren.")
    if not short.startswith("EA"):
        print("⚠ Hinweis: User-Tokens beginnen normalerweise mit 'EAA…'. Fahre trotzdem fort …")

    # Schritt 1: in langlebiges User-Token tauschen
    print("→ 1/3  Tausche in langlebiges User-Token …")
    data, err = _get("/oauth/access_token", {
        "grant_type": "fb_exchange_token", "client_id": app_id,
        "client_secret": app_secret, "fb_exchange_token": short})
    if err:
        fail("Tausch fehlgeschlagen: " + err +
             "\n  → Token frisch? (kurzlebige laufen in ~1-2h ab) · App-ID/Secret korrekt?")
    ll_user = data.get("access_token")
    if not ll_user:
        fail("Kein langlebiges User-Token erhalten: " + json.dumps(data)[:300])
    print("  ✓ langlebiges User-Token erhalten (gültig ~60 Tage).")

    # Schritt 2: Page-Token aus /me/accounts
    print("→ 2/3  Hole Page-Token aus /me/accounts …")
    data, err = _get("/me/accounts", {"access_token": ll_user, "limit": 200,
                                      "fields": "id,name,access_token"})
    if err:
        fail("/me/accounts fehlgeschlagen: " + err)
    pages = data.get("data", [])
    if not pages:
        fail("Keine Seiten zurückgegeben. Meist: Scope **pages_show_list** fehlt, oder du bist "
             "nicht Admin der Seite, oder im Explorer wurde die App/Scopes nicht übernommen.")
    by_id = {p.get("id"): p for p in pages}
    target = by_id.get(page_id)
    if not target:
        print("  Verfügbare Seiten (gesuchte ID %s nicht dabei):" % page_id)
        for p in pages:
            print("    - %s  ·  %s" % (p.get("id"), p.get("name")))
        fail("Seite %s nicht in der Liste. Richtige ID nehmen (oben) oder FB_PAGE_ID setzen." % page_id)
    page_token = target.get("access_token")
    if not page_token:
        fail("Seite gefunden (%s), aber kein access_token — fehlt **pages_manage_posts**/Admin-Rechte?"
             % target.get("name"))
    print("  ✓ Page-Token für Seite %s (%s) erhalten." % (target.get("name"), page_id))

    # Schritt 3: prüfen (Type=PAGE, Expires=Never)
    print("→ 3/3  Prüfe Token (Type + Ablauf) …")
    app_token = "%s|%s" % (app_id, app_secret)
    data, err = _get("/debug_token", {"input_token": page_token, "access_token": app_token})
    never = False; ttype = "?"
    if not err:
        d = data.get("data", {})
        ttype = d.get("type", "?")
        exp = d.get("expires_at", None)
        never = (exp == 0)
        scopes = d.get("scopes", [])
        print("  Type: %s · Expires: %s" % (ttype, "Never" if never else exp))
        if "pages_manage_posts" not in scopes:
            print("  ⚠ Scope pages_manage_posts NICHT im Token — Posten wird scheitern.")
    else:
        print("  (Prüfung übersprungen: " + err[:160] + ")")

    print("\n" + "=" * 64)
    print("FERTIG. Page-Token (als GitHub-Secret FB_PAGE_ACCESS_TOKEN setzen):\n")
    print(page_token)
    print("=" * 64)
    if not (ttype == "PAGE" and never):
        print("⚠ ACHTUNG: Erwartet wurde Type=PAGE + Expires=Never. Wenn nicht, oben die Hinweise prüfen.")
    print("Repo → Settings → Secrets and variables → Actions:")
    print("  FB_PAGE_ACCESS_TOKEN = <obiges Token>")
    print("  META_ACCESS_TOKEN    = <dasselbe Token>   (Fallback)")


if __name__ == "__main__":
    main()
