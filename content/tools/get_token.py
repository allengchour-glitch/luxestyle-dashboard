#!/usr/bin/env python3
"""
TikTok Marketing API – Access-Token holen (OAuth Code -> Token)

Tauscht app_id + secret + auth_code gegen einen langlebigen access_token.
Zeigt zusätzlich die advertiser_ids, auf die der Token Zugriff hat.

So kommst du an die 3 Werte (einmalig, im Browser):
  1) business-api.tiktok.com/portal -> deine App  ->  App ID + Secret
  2) In der App die Scopes aktivieren: "Ad Account Management" + "Creative Management"
  3) Authorization-URL der App im Browser öffnen -> Werbekonto zustimmen
     -> du wirst auf deine Redirect-URL geleitet, dort steht ?auth_code=XXXX
     (auth_code ist nur ~10 Min gültig -> zügig einlösen)

Nutzung (interaktiv – sicher, nichts landet im Verlauf):
    python get_token.py
Oder direkt:
    python get_token.py --app-id 123 --secret abc --auth-code xyz

Nur Standardbibliothek.
"""
import sys, json, argparse, urllib.request, urllib.error
try:
    from getpass import getpass
except Exception:
    getpass = input

URL = "https://business-api.tiktok.com/open_api/v1.3/oauth2/access_token/"

def get_token(app_id, secret, auth_code):
    body = json.dumps({"app_id": app_id, "secret": secret, "auth_code": auth_code}).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"_http_error": e.code, "_body": e.read().decode()[:1000]}

def main():
    ap = argparse.ArgumentParser(description="TikTok Marketing API – Access-Token holen")
    ap.add_argument("--app-id"); ap.add_argument("--secret"); ap.add_argument("--auth-code")
    a = ap.parse_args()

    app_id = a.app_id or input("App ID: ").strip()
    secret = a.secret or getpass("App Secret (wird nicht angezeigt): ").strip()
    auth_code = a.auth_code or input("auth_code (aus der Redirect-URL): ").strip()
    if not (app_id and secret and auth_code):
        sys.exit("Abbruch: app_id, secret und auth_code werden alle benötigt.")

    res = get_token(app_id, secret, auth_code)
    if res.get("_http_error"):
        sys.exit("HTTP %s: %s" % (res["_http_error"], res["_body"]))
    if res.get("code") not in (0, None):
        sys.exit("TikTok-Fehler %s: %s\n(auth_code abgelaufen? Scopes fehlen? Secret falsch?)"
                 % (res.get("code"), res.get("message")))

    data = res.get("data", {})
    token = data.get("access_token")
    advs = data.get("advertiser_ids") or []
    scope = data.get("scope")
    print("\n✅ Access-Token erhalten!\n")
    print("ACCESS_TOKEN :", token)
    print("ADVERTISER_IDS:", ", ".join(advs) if advs else "(keine – Konto evtl. nicht verknüpft)")
    if scope: print("SCOPES       :", scope)
    print("\n--- Nächster Schritt (PowerShell) ---")
    print('$env:TIKTOK_ACCESS_TOKEN="%s"' % (token or "DEIN_TOKEN"))
    print('$env:TIKTOK_ADVERTISER_ID="%s"' % (advs[0] if advs else "DEINE_ID"))
    print('python tiktok_upload.py ..\\ads\\LuxeStyle_Mix_Reel_Sommer.mp4 --name "LuxeStyle Mix Sommer"')
    print("\n(Token sicher aufbewahren, nicht teilen/committen.)")

if __name__ == "__main__":
    main()
