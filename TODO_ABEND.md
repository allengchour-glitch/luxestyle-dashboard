# LuxeStyle · To-do heute Abend (Stand 2026-06-09)

Alles hier sind Schritte, die **nur du** machen kannst (Login/Tokens/Secrets/Käufe).
Technik ist geprüft & bereit: Storefront optimiert, Checkout funktioniert, Pixel feuern,
10 Klaviyo-Flows live. Einziger Engpass: **Traffic + Capture + erster Verkauf.**

## Umsatz-Hebel zuerst
- [ ] **TikTok anwerfen** — Entwurf raushauen (Profil → Entwürfe → Posten) + 1 Reel aus der Reihe (Tag 1 = `LuxeStyle_NeuDamen_AdSafe.mp4`), **Trending-Sound** drüberlegen. (414 Follower = Reichweite ist da.)
- [ ] **Warmes Netzwerk** — 20–30 Leute per WhatsApp/Story: Shop-Link + Code **WELCOME10**. Bringt fast immer die ersten Verkäufe.
- [ ] **Klaviyo-Popup live** — Klaviyo → Sign-up Forms → Popup „10% mit WELCOME10" → Ziel-Liste „Email List" → Publish. Vorher Onsite/Shopify-Integration an. (Details: `content/KLAVIYO_CAPTURE_SETUP.md`.) Schließt den Signup-Leak (aktuell 1 Abonnent).

## Wenn noch Zeit (Infrastruktur)
- [ ] **FB-Secret setzen** — `FB_PAGE_ACCESS_TOKEN` (+ `META_ACCESS_TOKEN`) im Repo `luxestyle-dashboard` (Settings → Secrets and variables → Actions). Token-Helfer: `content/tools/fb-token-helper.html`. Dann postet FB automatisch mit.
- [ ] **PR #31 → `main` mergen** — damit der geplante Auto-Poster (`luxestyle-social.yml`, 2×/Tag) läuft (geplante Workflows laufen nur auf `main`).
- [ ] **aban-news live** — `abannews.com` via **Netlify** (gratis, Repo bleibt privat) statt GitHub-Pages-Upgrade. ODER: neue Cloud-Session auf `aban-news-landing` starten → dann richtet Claude Netlify + DNS Schritt für Schritt ein.

## Reels (liegen auf dem Handy + in `content/ads/`)
Tag 1 NeuDamen · 2 Sommer · 3 FürSie · 4 Tech · 5 Wellness · 6 Reise · 7 GeschenkeIhn.
Captions je Reel in `content/tools/captions.json`. 7-Tage-Plan: `content/POSTING_PLAN_7TAGE.md`.

## NICHT diese Woche
- Keine bezahlten Ads (erst wenn organisch + Capture laufen).
- Kein Auto-Follow / gekaufte Follower (Sperr-Risiko).
- Nicht weiter an Flows/Technik polieren — die ist fertig.
