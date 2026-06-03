#!/usr/bin/env python3
"""
LuxeStyle TikTok-Kampagnen-Builder  —  legt eine komplette Anzeige per **TikTok
Marketing API** an: Kampagne -> Ad Group -> Ad. Erspart das Durchklicken im Ads
Manager (genau der Flow, der zuletzt den DPA-/Bid-Fehler warf).

Bewusste LuxeStyle-Defaults (alle per CLI überschreibbar):
  • Ziel: WEB_CONVERSIONS (Website, KEIN Katalog/DPA -> kein DpaAudienceTypeRender-Fehler)
  • Bid: BID_TYPE_NO_BID = **Lowest Cost / Maximum Delivery** -> KEIN Target-CPA nötig
    (löst „Set a bid price"); TikTok holt mit dem Budget die meisten Conversions
  • Optimierung: Add-to-Cart (wenig Daten-freundlich; später Complete Payment)
  • Targeting: Schweiz, alle Alter, Sprachen DE+FR, broad
  • Budget: CHF 20/Tag · Placement: nur TikTok
  • **Erstellt alles PAUSIERT** (operation_status=DISABLE) -> du prüfst im Ads
    Manager und schaltest selbst scharf. Kein versehentliches Ausgeben.

Pipeline:  build_reel.py -> tiktok_upload.py (video_id) -> tiktok_campaign.py
   ODER direkt:  tiktok_campaign.py --video ../ads/LuxeStyle_Sommer_AdSafe.mp4

ENV (nichts committen!):
  TIKTOK_ACCESS_TOKEN   = Token einer genehmigten App mit Scopes
                          **Ads Management** + **Creative Management**
  TIKTOK_ADVERTISER_ID  = Werbekonto-ID

Beispiele:
  python tiktok_campaign.py --video ../ads/LuxeStyle_Sommer_AdSafe.mp4 \
      --text "Entdecke LuxeStyle – Premium aus der Schweiz. 10% mit WELCOME10."
  python tiktok_campaign.py --video-id 1234567890 --budget 30 --event COMPLETE_PAYMENT
  python tiktok_campaign.py --video ../ads/LuxeStyle_Sommer_AdSafe.mp4 --dry-run

Nur Standardbibliothek. Wiederverwendet Upload aus tiktok_upload.py.
Hinweis: TikTok ändert Enums/Pflichtfelder je API-Version — bei Fehlern die
zurückgegebene message lesen; Felder via --set key=value anpassbar.
"""
import os, sys, json, argparse, urllib.parse, urllib.request, urllib.error

BASE = "https://business-api.tiktok.com/open_api/v1.3"
PIXEL_DEFAULT = "D8EQE4JC77UAEKHUJCM0"   # luxestyle.ch
LANDING_DEFAULT = "https://luxestyle.ch"

# Optimierungs-Event -> TikTok-Enum (Website-Conversions, Pixel)
EVENT_MAP = {
    "ADD_TO_CART": "ON_WEB_ADD_TO_CART",
    "VIEW_CONTENT": "ON_WEB_DETAIL",
    "INITIATE_CHECKOUT": "INITIATE_CHECKOUT",
    "COMPLETE_PAYMENT": "ON_WEB_ORDER",
    "PURCHASE": "ON_WEB_ORDER",
}


def creds():
    tok = os.environ.get("TIKTOK_ACCESS_TOKEN")
    adv = os.environ.get("TIKTOK_ADVERTISER_ID")
    if not (tok and adv):
        sys.exit("Bitte ENV setzen:\n  TIKTOK_ACCESS_TOKEN=...\n  TIKTOK_ADVERTISER_ID=...\n"
                 "(App-Scopes: Ads Management + Creative Management.)")
    return tok, adv


def _api(method, path, token, json_body=None, params=None):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    headers = {"Access-Token": token}
    data = None
    if json_body is not None:
        data = json.dumps(json_body).encode(); headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            out = json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit("HTTP %s: %s" % (e.code, e.read().decode()[:800]))
    if out.get("code") not in (0, None):
        sys.exit("TikTok-API-Fehler %s: %s\n(Scope fehlt? Pflichtfeld/Enum falsch? Token gültig?)"
                 % (out.get("code"), out.get("message")))
    return out.get("data", {})


# ---------- Helfer: Identity, Region, Cover, Video-Upload ----------
def find_identity(token, adv):
    """Erste verfügbare Werbe-Identity (für die Ad-Ebene Pflicht)."""
    d = _api("GET", "/identity/get/", token, params={"advertiser_id": adv})
    lst = d.get("identity_list") or d.get("list") or []
    if not lst:
        sys.exit("Keine Identity gefunden. Im Ads Manager unter 'Identity' eine LuxeStyle-Identity "
                 "anlegen (oder TikTok-Konto verknüpfen), dann erneut.")
    it = lst[0]
    return it.get("identity_id"), it.get("identity_type", "CUSTOMIZED_USER")


def find_region(token, adv, name="Switzerland"):
    """location_id der Schweiz (für Targeting)."""
    d = _api("GET", "/tool/region/", token, params={"advertiser_id": adv, "placements": json.dumps(["PLACEMENT_TIKTOK"])})
    for r in d.get("region_info") or d.get("list") or []:
        if str(r.get("name", "")).lower() == name.lower():
            return str(r.get("region_id") or r.get("location_id"))
    sys.exit("Region '%s' nicht gefunden (über /tool/region/). Mit --location <id> setzen." % name)


def suggest_cover(token, adv, video_id):
    """Auto-Cover-Bild-ID zum Video (Ad braucht ein Cover)."""
    try:
        d = _api("GET", "/file/video/suggestcover/", token, params={"advertiser_id": adv, "video_id": video_id})
        covers = d.get("list") or []
        return covers[0].get("id") if covers else None
    except SystemExit:
        return None


def upload_video(token, adv, path):
    """Video hochladen via tiktok_upload.py (gleicher Ordner) -> video_id."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        from tiktok_upload import upload_by_file
    except Exception as e:
        sys.exit("Konnte tiktok_upload.py nicht laden (%s). --video-id stattdessen nutzen." % e)
    res = upload_by_file(token, adv, path, os.path.basename(path))
    data = res.get("data", {})
    item = (data.get("list") or [data])[0] if isinstance(data, dict) else {}
    vid = item.get("video_id") or data.get("video_id")
    if not vid:
        sys.exit("Upload lieferte keine video_id: %s" % json.dumps(res)[:400])
    print("  video hochgeladen -> video_id:", vid)
    return vid


# ---------- Kampagne / Ad Group / Ad ----------
def create_campaign(token, adv, name, status):
    body = {"advertiser_id": adv, "campaign_name": name,
            "objective_type": "WEB_CONVERSIONS",
            "budget_mode": "BUDGET_MODE_INFINITE",   # Budget steuern wir auf Ad-Group-Ebene
            "operation_status": status}
    return _api("POST", "/campaign/create/", token, json_body=body)["campaign_id"]


def create_adgroup(token, adv, campaign_id, name, pixel, event, location_id, budget, status):
    body = {
        "advertiser_id": adv, "campaign_id": campaign_id, "adgroup_name": name,
        "promotion_type": "WEBSITE",
        "placement_type": "PLACEMENT_TYPE_NORMAL", "placements": ["PLACEMENT_TIKTOK"],
        "pixel_id": pixel, "optimization_event": EVENT_MAP.get(event, event),
        "optimization_goal": "CONVERT",
        "location_ids": [location_id],
        "gender": "GENDER_UNLIMITED",
        "age_groups": ["AGE_18_24", "AGE_25_34", "AGE_35_44", "AGE_45_54", "AGE_55_100"],
        "languages": ["de", "fr"],
        "budget_mode": "BUDGET_MODE_DAY", "budget": float(budget),
        "schedule_type": "SCHEDULE_FROM_NOW",
        "billing_event": "OCPM",
        "bid_type": "BID_TYPE_NO_BID",            # Lowest Cost / Max Delivery -> KEIN Target-CPA
        "pacing": "PACING_MODE_SMOOTH",
        "operation_status": status,
    }
    return _api("POST", "/adgroup/create/", token, json_body=body)["adgroup_id"]


def create_ad(token, adv, adgroup_id, name, identity_id, identity_type, video_id, cover_id, text, cta, url, status):
    creative = {
        "ad_name": name, "identity_id": identity_id, "identity_type": identity_type,
        "ad_format": "SINGLE_VIDEO", "video_id": video_id,
        "ad_text": text, "call_to_action": cta, "landing_page_url": url,
    }
    if cover_id:
        creative["image_ids"] = [cover_id]
    body = {"advertiser_id": adv, "adgroup_id": adgroup_id, "creatives": [creative]}
    d = _api("POST", "/ad/create/", token, json_body=body)
    ids = d.get("ad_ids") or []
    return ids[0] if ids else None


def main():
    ap = argparse.ArgumentParser(description="TikTok: komplette Anzeige anlegen (Kampagne+AdGroup+Ad)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--video", help="MP4 hochladen und verwenden")
    g.add_argument("--video-id", help="bereits hochgeladene video_id (aus tiktok_upload.py)")
    ap.add_argument("--name", default="LuxeStyle CH – Sommer", help="Basisname für Kampagne/AdGroup/Ad")
    ap.add_argument("--text", default="Entdecke LuxeStyle – Premium Accessoires aus der Schweiz. 10% mit Code WELCOME10.",
                    help="Anzeigentext (ad-safe halten)")
    ap.add_argument("--cta", default="SHOP_NOW", help="Call-to-Action (SHOP_NOW, LEARN_MORE, ...)")
    ap.add_argument("--url", default=LANDING_DEFAULT, help="Landing-Page-URL")
    ap.add_argument("--pixel", default=PIXEL_DEFAULT, help="Pixel-ID")
    ap.add_argument("--event", default="ADD_TO_CART",
                    help="Optimierung: ADD_TO_CART | VIEW_CONTENT | INITIATE_CHECKOUT | COMPLETE_PAYMENT")
    ap.add_argument("--budget", default="20", help="Tagesbudget (CHF), Default 20")
    ap.add_argument("--location", help="Region/location_id (Default: Schweiz auto)")
    ap.add_argument("--live", action="store_true",
                    help="Anzeige SOFORT aktiv schalten (Default: pausiert erstellen, du prüfst zuerst)")
    ap.add_argument("--dry-run", action="store_true", help="nur die Payloads zeigen, nichts erstellen")
    a = ap.parse_args()

    status = "ENABLE" if a.live else "DISABLE"

    if a.dry_run:
        print("DRY-RUN — würde anlegen:")
        print("  Kampagne :", a.name, "(WEB_CONVERSIONS, Budget auf AdGroup)")
        print("  AdGroup  : Schweiz · DE+FR · alle Alter · Pixel %s · Event %s · CHF %s/Tag · Lowest-Cost (kein Target-CPA)"
              % (a.pixel, a.event, a.budget))
        print("  Ad       : SINGLE_VIDEO · CTA %s · %s" % (a.cta, a.url))
        print("  Status   :", status, "(pausiert = du schaltest selbst scharf)" if status == "DISABLE" else "(SOFORT aktiv!)")
        print("  Text     :", a.text)
        if a.video: print("  Video    : Upload", a.video)
        if a.video_id: print("  Video    : video_id", a.video_id)
        return

    if not (a.video or a.video_id):
        sys.exit("Bitte --video <mp4> ODER --video-id <id> angeben (oder --dry-run).")

    token, adv = creds()
    print("→ Identity & Region holen ...")
    identity_id, identity_type = find_identity(token, adv)
    location_id = a.location or find_region(token, adv, "Switzerland")
    print("  identity:", identity_id, "· region:", location_id)

    if a.video:
        if not os.path.exists(a.video): sys.exit("Datei fehlt: " + a.video)
        print("→ Video hochladen ...")
        video_id = upload_video(token, adv, a.video)
    else:
        video_id = a.video_id
    cover_id = suggest_cover(token, adv, video_id)

    print("→ Kampagne anlegen ...")
    campaign_id = create_campaign(token, adv, a.name, status)
    print("  campaign_id:", campaign_id)
    print("→ Ad Group anlegen ...")
    adgroup_id = create_adgroup(token, adv, campaign_id, a.name + " – AdGroup",
                                a.pixel, a.event, location_id, a.budget, status)
    print("  adgroup_id:", adgroup_id)
    print("→ Ad anlegen ...")
    ad_id = create_ad(token, adv, adgroup_id, a.name + " – Ad", identity_id, identity_type,
                      video_id, cover_id, a.text, a.cta, a.url, status)
    print("  ad_id:", ad_id)

    print("\n✅ Fertig. Anzeige ist %s." % ("AKTIV" if status == "ENABLE" else "PAUSIERT erstellt"))
    if status == "DISABLE":
        print("   -> Im TikTok Ads Manager prüfen und auf AKTIV schalten (oder erneut mit --live).")
    print("   Pixel:", a.pixel, "· Optimierung:", a.event, "· Budget: CHF", a.budget, "/Tag · Lowest Cost.")


if __name__ == "__main__":
    main()
