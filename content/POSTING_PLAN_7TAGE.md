# LuxeStyle · 7-Tage-Start-Plan (erster Kunde / erste Anmeldungen)

**Stand (live verifiziert, 2026-06-09):** Storefront optimiert (PDP-Reihenfolge/Preis), **Checkout funktioniert**
(Shop Pay/PayPal/Google Pay, E-Mail-Opt-in vorab an), **Meta- + TikTok- + Google-Pixel feuern**.
Klaviyo: **10 Flows live** (Welcome, Abandoned Cart/Checkout, Win-Back, Post-Purchase) — warten nur auf Publikum.
Engpass = **Traffic + Anmeldungen**. Genau das adressiert dieser Plan.

> Ziel der Woche: **1–3 erste Bestellungen** (warmes Netzwerk) + **erste ~30–50 E-Mail-Anmeldungen** (Popup + Posts).
> Code überall: **WELCOME10**. Link in allen Bios: **luxestyle.ch**.

## Tägliche Routine (~25 Min)
1. **1 Reel posten** (siehe Tabelle) — TikTok zuerst (Trending-Sound drüberlegen), dann IG-Reel, FB, Threads.
2. **15 Min Interaktion**: in deiner Nische 10–15 Kommentare/Likes, auf Kommentare antworten (Antworten-Bank im Content-Tab).
3. **Story** mit Produkt + „Link in Bio" + WELCOME10.

## Einmal diese Woche (höchste Hebelwirkung zuerst)
- **Tag 1 – Warmes Netzwerk:** 20–30 Leute persönlich (WhatsApp/Story) anschreiben: kurzer Satz + Shop-Link + WELCOME10.
  Das bringt fast immer die **ersten Verkäufe** und sofort echte Daten (Pixel/Checkout/erste Reviews).
- **Klaviyo-Popup live schalten** (5–10 Min, siehe `KLAVIYO_CAPTURE_SETUP.md`) — sonst verpufft jeder Besucher ohne Anmeldung.

## Reel-Plan (Reels liegen in `content/ads/`, Captions in `content/tools/captions.json`)
| Tag | Reel | Thema | Beste Zeit (CH) |
|----|------|-------|-----------------|
| 1 | `LuxeStyle_NeuDamen_AdSafe.mp4` | Neu · Damen-Sommer | 19:00 |
| 2 | `LuxeStyle_Sommer_AdSafe.mp4` | Sommer-Mix | 12:00 + 19:00 |
| 3 | `LuxeStyle_FuerSie_AdSafe.mp4` | Für Sie · Schmuck | 19:00 |
| 4 | `LuxeStyle_Tech_AdSafe.mp4` | Tech & Gadgets | 19:00 |
| 5 | `LuxeStyle_Wellness_AdSafe.mp4` | Wellness & Zuhause | 12:00 |
| 6 | `LuxeStyle_Reise_AdSafe.mp4` | Sommer & Reise | 19:00 |
| 7 | `LuxeStyle_Geschenke_Ihn_AdSafe.mp4` | Geschenke für ihn | 19:00 |

Die fertigen Captions (mit WELCOME10 + Hashtags) stehen je Reel in `captions.json` — der Multi-Kanal-Poster
`post_next_reel.py` nimmt Index = Reihenfolge. **Manuell** geht es genauso: Reel + Caption hochladen.

## Posten: automatisch vs. manuell
- **Automatisch** (sobald Tokens als GitHub-Secrets gesetzt): Workflow `luxestyle-social.yml` (2×/Tag).
  - FB: `FB_PAGE_ACCESS_TOKEN` (Page-Token-Helfer fertig). IG: `IG_ACCESS_TOKEN`+`IG_USER_ID=17841480560863361`.
    Threads: `THREADS_ACCESS_TOKEN`. TikTok-Entwurf: `TIKTOK_OPEN_ACCESS_TOKEN`. Telegram: `TELEGRAM_*`.
  - ⚠️ Repo privat → für FB/IG/Threads **öffentliche CDN-URL** statt GitHub-Raw (siehe `shopify-product-videos.json`).
- **Manuell** (zuverlässig, sofort): Reel aus `content/ads/` + Caption aus `captions.json` direkt in die App.
  Für TikTok-Reichweite: **Trending-Sound** in der App drüberlegen.

## Diese Woche NICHT
- Keine bezahlten Ads, bis A–C laufen + ein compliant Creative steht (dann CHF 5–10/Tag Test).
- Kein Auto-Follow / keine gekauften Follower (Sperr-Risiko).
- Posting-Tempo moderat (1–2/Tag), Konten sind jung.
