#!/usr/bin/env python3
"""
OAuth-Helfer für die ORGANISCHEN Post-Tools (nicht die Ads-API).

  python get_open_token.py tiktok   -> TikTok Login-Kit: auth_code -> access_token (+ refresh, open_id, scope)
  python get_open_token.py meta     -> Meta: Short-Lived -> Long-Lived-Token + listet IG-Business-Account-IDs

TikTok (developers.tiktok.com -> App -> Login Kit + Content Posting API):
  Scopes aktivieren: video.upload (Entwurf) bzw. video.publish (Direkt, nach Audit).
  Authorize-URL im Browser öffnen -> Redirect enthält ?code=XXXX (kurz gültig) -> hier eingeben.

Meta (developers.facebook.com -> App; IG-Business-Konto mit FB-Seite verknüpft):
  Graph API Explorer -> User-Token mit instagram_business_basic + instagram_business_content_publish
  + pages_show_list -> Short-Lived-Token hier eintauschen.

Nur Standardbibliothek. Secrets danach als ENV/GitHub-Secret setzen, NICHT committen.
"""
import sys, json, argparse, urllib.parse, urllib.request, urllib.error
try:
    from getpass import getpass
except Exception:
    getpass = input


def _get(url):
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"_http_error": e.code, "_body": e.read().decode()[:800]}


def _post_form(url, params):
    data = urllib.parse.urlencode(params).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"_http_error": e.code, "_body": e.read().decode()[:800]}


def tiktok():
    ck = input("TikTok Client Key: ").strip()
    cs = getpass("TikTok Client Secret (versteckt): ").strip()
    code = input("auth_code (aus Redirect ?code=…): ").strip()
    redirect = input("Redirect-URI (exakt wie in der App): ").strip()
    res = _post_form("https://open.tiktokapis.com/v2/oauth/token/", {
        "client_key": ck, "client_secret": cs, "code": code,
        "grant_type": "authorization_code", "redirect_uri": redirect})
    if res.get("_http_error"):
        sys.exit("HTTP %s: %s" % (res["_http_error"], res["_body"]))
    if not res.get("access_token"):
        sys.exit("Fehler: " + json.dumps(res)[:600])
    print("\n✅ TikTok-Token erhalten")
    print("ACCESS_TOKEN :", res.get("access_token"))
    print("REFRESH      :", res.get("refresh_token"))
    print("SCOPES       :", res.get("scope"))
    print("\n$env:TIKTOK_OPEN_ACCESS_TOKEN=\"%s\"   (Windows)" % res.get("access_token"))
    print("export TIKTOK_OPEN_ACCESS_TOKEN=\"%s\"   (Linux/macOS)" % res.get("access_token"))


def meta():
    app_id = input("Meta App ID: ").strip()
    secret = getpass("Meta App Secret (versteckt): ").strip()
    short = input("Short-Lived User-Token (Graph Explorer): ").strip()
    ll = _get("https://graph.facebook.com/v21.0/oauth/access_token?" + urllib.parse.urlencode({
        "grant_type": "fb_exchange_token", "client_id": app_id,
        "client_secret": secret, "fb_exchange_token": short}))
    if ll.get("_http_error") or not ll.get("access_token"):
        sys.exit("Long-Lived-Tausch fehlgeschlagen: " + json.dumps(ll)[:600])
    tok = ll["access_token"]
    print("\n✅ Long-Lived-Token erhalten (gültig ~60 Tage):\n", tok)
    # IG-Business-Account über die FB-Seiten finden
    pages = _get("https://graph.facebook.com/v21.0/me/accounts?" + urllib.parse.urlencode({
        "fields": "name,instagram_business_account", "access_token": tok}))
    print("\nVerknüpfte Seiten / IG-Accounts:")
    for p in pages.get("data", []):
        iba = (p.get("instagram_business_account") or {}).get("id")
        print("  Seite: %-28s IG_USER_ID: %s" % (p.get("name"), iba or "(keine IG-Business-Verknüpfung)"))
    print("\nSetze dann: IG_ACCESS_TOKEN=<Token oben>  ·  IG_USER_ID=<die ID>")


def threads():
    """Threads-API: Short-Lived -> Long-Lived (60 Tage) + Threads-User-ID via /me."""
    secret = getpass("Threads App Secret (versteckt): ").strip()
    short = input("Short-Lived Threads-Token (aus dem App-Dashboard 'Generate token'): ").strip()
    ll = _get("https://graph.threads.net/access_token?" + urllib.parse.urlencode({
        "grant_type": "th_exchange_token", "client_secret": secret, "access_token": short}))
    if ll.get("_http_error") or not ll.get("access_token"):
        sys.exit("Long-Lived-Tausch fehlgeschlagen: " + json.dumps(ll)[:600])
    tok = ll["access_token"]
    print("\n✅ Long-Lived Threads-Token (gültig ~60 Tage):\n", tok)
    me = _get("https://graph.threads.net/v1.0/me?" + urllib.parse.urlencode({
        "fields": "id,username", "access_token": tok}))
    uid = me.get("id")
    print("\nThreads-Konto:", "@" + me.get("username", "?"), "· THREADS_USER_ID:", uid or "(nicht gefunden)")
    print("\nSetze als GitHub-Secrets:")
    print("  THREADS_ACCESS_TOKEN=<Token oben>")
    print("  THREADS_USER_ID=%s" % (uid or "<die ID>"))


def main():
    ap = argparse.ArgumentParser(description="OAuth-Helfer für organische Post-Tools")
    ap.add_argument("provider", choices=["tiktok", "meta", "threads"])
    a = ap.parse_args()
    if a.provider == "tiktok": tiktok()
    elif a.provider == "threads": threads()
    else: meta()


if __name__ == "__main__":
    main()
