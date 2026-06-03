#!/usr/bin/env python3
"""
LuxeStyle Reel-/Ad-Builder  —  TikTok-Premium Automatisierungs-Tool (v3)

Aus einer JSON-Konfig automatisch fertige, gebrandete 9:16-Reels/Ads:
  • Shopify-AUTO-MODUS: nur Produkt-Handles ODER einen Filter (tag/typ/preis…) angeben
    -> Tool zieht Titel, Preis & Bild selbst per Admin-API (kein manuelles Manifest)
  • A/B-HOOKS: mehrere Hook-Varianten -> mehrere Output-Dateien (_A/_B/_C) für Ad-Tests
  • Blur-Fill, animierte Captions (Fade), jitterfreier Ken-Burns, Premium-Transitions
  • Hook-Karte, Social-Proof (gezeichnete Sterne), Story-Progress-Bar, Preis-Badge
  • Musik-Moods (calm/upbeat, lizenzfrei), konfigurierbare Markenfarbe
  • Export 1080x1920 H.264 yuv420p +faststart (TikTok/IG/YT-ready)

Nutzung:
  python3 build_reel.py manifest.json [--out out.mp4]
  python3 build_reel.py --shopify handle1,handle2,handle3 [--out out.mp4]
  python3 build_reel.py --shopify-query "tag:sommer-2026" --limit 6

Shopify-Auto braucht ENV:  SHOPIFY_STORE=xxxx.myshopify.com  SHOPIFY_ADMIN_TOKEN=shpat_...
Abhängigkeiten: Pillow, imageio-ffmpeg
"""
import json, os, sys, math, tempfile, subprocess, urllib.request, argparse

# ---------- ffmpeg + Font ----------
def find_ffmpeg():
    try:
        import imageio_ffmpeg; return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        from shutil import which
        exe = which("ffmpeg")
        if exe: return exe
        sys.exit("ffmpeg nicht gefunden – `pip install imageio-ffmpeg`.")

def first_existing(paths):
    for p in paths:
        if p and os.path.exists(p): return p
    return None

_WIN = os.environ.get("WINDIR", "C:\\Windows")
FONT = first_existing([
    os.environ.get("LUXE_FONT"),
    "/mnt/skills/examples/canvas-design/canvas-fonts/BigShoulders-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    os.path.join(_WIN, "Fonts", "arialbd.ttf"), os.path.join(_WIN, "Fonts", "segoeuib.ttf"),
    os.path.join(_WIN, "Fonts", "arial.ttf"),
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial.ttf",
])
if not FONT:
    sys.exit("Keine TTF-Font gefunden. Setze LUXE_FONT=...\\arialbd.ttf oder installiere DejaVu/Liberation.")
FF = find_ffmpeg()
W, H = 1080, 1920

def has_filter(name):
    try:
        return (" %s " % name) in subprocess.run([FF, "-hide_banner", "-filters"],
                                                  capture_output=True, text=True).stdout
    except Exception:
        return False
HAS_DRAWBOX = has_filter("drawbox")

def run(args):
    r = subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", *args], capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-2000:] + "\n"); raise SystemExit("ffmpeg-Fehler")

def fetch(src, wd):
    if src.startswith(("http://", "https://")):
        ext = os.path.splitext(src.split("?")[0])[1] or ".img"
        dst = os.path.join(wd, "src_%d%s" % (abs(hash(src)) % 999999, ext))
        urllib.request.urlretrieve(src, dst); return dst
    if not os.path.exists(src): raise SystemExit("Datei fehlt: " + src)
    return src

def hexrgb(s, d=(201, 162, 75)):
    if not s: return d
    s = s.lstrip("#")
    try: return tuple(int(s[i:i+2], 16) for i in (0, 2, 4))
    except Exception: return d

def clean_title(t, maxlen=26):
    for sep in ("·", "("):
        if sep in t: t = t.split(sep)[0]
    t = t.strip(" -–—")
    return (t[:maxlen-1] + "…") if len(t) > maxlen else t

# ---------- Shopify Admin-API ----------
PRODUCTS_QUERY = """
query Q($q:String!,$n:Int!,$sk:ProductSortKeys,$rev:Boolean){
  products(first:$n, query:$q, sortKey:$sk, reverse:$rev){
    edges{ node{
      handle title status publishedAt
      priceRangeV2{ minVariantPrice{ amount currencyCode } }
      media(first:6){ edges{ node{ ... on MediaImage { image{ url } } } } }
    }}
  }
}"""
SORT_MAP = {"created": "CREATED_AT", "price": "PRICE", "title": "TITLE",
            "updated": "UPDATED_AT", "best": "BEST_SELLING", "relevance": "RELEVANCE"}

def shopify_gql(store, token, query, variables):
    url = "https://%s/admin/api/2024-10/graphql.json" % store
    data = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Content-Type": "application/json", "X-Shopify-Access-Token": token})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def shopify_resolve(sp):
    """Filter/Handles -> Items (Titel, Preis, Bild) per Admin-API. Gibt (items, warnings)."""
    store = sp.get("store") or os.environ.get("SHOPIFY_STORE")
    token = os.environ.get("SHOPIFY_ADMIN_TOKEN")
    if not (store and token):
        sys.exit("Shopify-Auto braucht ENV SHOPIFY_STORE (xxxx.myshopify.com) + SHOPIFY_ADMIN_TOKEN (shpat_…).")
    handles = sp.get("handles"); query = sp.get("query")
    if handles:   q = " OR ".join('handle:%s' % h for h in handles)
    elif query:   q = query
    else:         sys.exit("shopify: 'handles' ODER 'query' (Filter) angeben.")
    sk = SORT_MAP.get((sp.get("sort") or "").lower())
    data = shopify_gql(store, token, PRODUCTS_QUERY,
                       {"q": q, "n": int(sp.get("limit", 8)), "sk": sk, "rev": bool(sp.get("reverse", False))})
    if data.get("errors"): sys.exit("Shopify-API-Fehler: %s" % data["errors"])
    edges = data["data"]["products"]["edges"]
    only_pub = sp.get("only_published", True); img_i = int(sp.get("img", 0))
    pfmt = sp.get("price_format", "{cur} {price}"); ddur = float(sp.get("default_dur", 1.7))
    exclude = set(sp.get("exclude", [])); items, warn, k = [], [], 0
    by_handle = {}
    for e in edges:
        n = e["node"]
        if n["handle"] in exclude: continue
        if only_pub and not n.get("publishedAt"):
            warn.append("übersprungen (nicht published): %s" % n["handle"]); continue
        imgs = [x["node"]["image"]["url"] for x in n["media"]["edges"] if x["node"].get("image")]
        if not imgs:
            warn.append("kein Bild: %s" % n["handle"]); continue
        mv = n["priceRangeV2"]["minVariantPrice"]
        sub = pfmt.format(price="%.2f" % float(mv["amount"]), cur=mv["currencyCode"], currency=mv["currencyCode"])
        it = {"title": clean_title(n["title"]), "sub": sub, "src": imgs[min(img_i, len(imgs)-1)],
              "dur": ddur, "zoom": "in" if k % 2 == 0 else "out"}
        by_handle[n["handle"]] = it; items.append(it); k += 1
    if handles:  # Reihenfolge der Handles beibehalten
        items = [by_handle[h] for h in handles if h in by_handle]
    return items, warn

# ---------- PIL Overlays ----------
def _pil():
    from PIL import Image, ImageDraw, ImageFont; return Image, ImageDraw, ImageFont
def _cx(d, t, f):
    b = d.textbbox((0, 0), t, font=f); return (W - (b[2]-b[0]))//2 - b[0]
def _sh(d, xy, t, f, fill, off=2, sh=(0, 0, 0, 170)):
    x, y = xy; d.text((x+off, y+off), t, font=f, fill=sh); d.text((x, y), t, font=f, fill=fill)
def _star(d, cxp, cyp, R, fill):
    r = R*0.42; pts = []
    for i in range(10):
        a = -math.pi/2 + i*math.pi/5; rad = R if i % 2 == 0 else r
        pts.append((cxp+rad*math.cos(a), cyp+rad*math.sin(a)))
    d.polygon(pts, fill=fill)

def ov_caption(brand, l1, l2, accent, out, badge=False):
    Image, ImageDraw, ImageFont = _pil(); GOLD = accent + (255,)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    fw, f1, f2 = ImageFont.truetype(FONT, 56), ImageFont.truetype(FONT, 50), ImageFont.truetype(FONT, 34)
    wm = " ".join(brand.upper()); _sh(d, (_cx(d, wm, fw), 96), wm, fw, (255, 255, 255, 240))
    yL = 1150; d.rectangle([(W-200)//2, yL, (W+200)//2, yL+4], fill=GOLD)
    if l1: _sh(d, (_cx(d, l1, f1), yL+22), l1, f1, (255, 255, 255, 255))
    if l2:
        if badge:
            b = d.textbbox((0, 0), l2, font=f2); tw = b[2]-b[0]
            d.rounded_rectangle([(W-tw)//2-26, yL+86, (W+tw)//2+26, yL+86+58], radius=29, fill=GOLD)
            _sh(d, (_cx(d, l2, f2), yL+92), l2, f2, (20, 16, 12, 255), sh=(0, 0, 0, 0))
        else:
            _sh(d, (_cx(d, l2, f2), yL+86), l2, f2, GOLD)
    img.save(out)

def ov_hook(brand, title, sub, accent, out):
    Image, ImageDraw, ImageFont = _pil(); GOLD = accent + (255,)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rectangle([0, 150, W, 650], fill=(15, 12, 10, 140))
    fw, ft, fs = ImageFont.truetype(FONT, 46), ImageFont.truetype(FONT, 116), ImageFont.truetype(FONT, 48)
    wm = " ".join(brand.upper()); _sh(d, (_cx(d, wm, fw), 190), wm, fw, (255, 255, 255, 235))
    _sh(d, (_cx(d, title, ft), 300), title, ft, (255, 255, 255, 255), off=3)
    d.rectangle([(W-300)//2, 470, (W+300)//2, 476], fill=GOLD)
    if sub: _sh(d, (_cx(d, sub, fs), 502), sub, fs, GOLD)
    img.save(out)

def card_proof(stars, title, sub, foot, accent, out):
    Image, ImageDraw, ImageFont = _pil(); GOLD = accent + (255,)
    ec = Image.new("RGB", (W, H), (17, 15, 14)); d = ImageDraw.Draw(ec)
    n = max(1, min(5, int(stars))); sx = W//2 - (n-1)*120//2
    for i in range(n): _star(d, sx+i*120, 600, 46, accent)
    f1, f2, f3 = ImageFont.truetype(FONT, 56), ImageFont.truetype(FONT, 40), ImageFont.truetype(FONT, 34)
    if title: _sh(d, (_cx(d, title, f1), 700), title, f1, (255, 255, 255))
    if sub:   _sh(d, (_cx(d, sub, f2), 790), sub, f2, (220, 220, 220))
    d.rectangle([(W-260)//2, 880, (W+260)//2, 885], fill=GOLD)
    if foot:  _sh(d, (_cx(d, foot, f3), 915), foot, f3, accent)
    ec.save(out)

def card_end(brand, code, domain, accent, out):
    Image, ImageDraw, ImageFont = _pil(); GOLD = accent + (255,)
    ec = Image.new("RGB", (W, H), (17, 15, 14)); d = ImageDraw.Draw(ec)
    fb, f1, f2 = ImageFont.truetype(FONT, 92), ImageFont.truetype(FONT, 50), ImageFont.truetype(FONT, 38)
    wm = " ".join(brand.upper()); _sh(d, (_cx(d, wm, fb), 700), wm, fb, (255, 255, 255), off=3, sh=(0, 0, 0, 150))
    d.rectangle([(W-260)//2, 852, (W+260)//2, 857], fill=GOLD)
    if code: _sh(d, (_cx(d, "Code %s = 10%%" % code, f1), 900), "Code %s = 10%%" % code, f1, accent)
    t = "Jetzt shoppen -> %s" % domain; _sh(d, (_cx(d, t, f2), 990), t, f2, (225, 225, 225))
    ec.save(out)

# ---------- Segmente ----------
CAP_FADE = "fade=t=in:st=0.05:d=0.45:alpha=1"

def seg_image(img, overlay, dur, zoom_in, out, fgw=1720):
    n = max(2, int(dur*30)); z = "1+0.07*on/%d" % n if zoom_in else "1.07-0.07*on/%d" % n
    still = out + ".png"
    run(["-i", img, "-frames:v", "1", "-filter_complex",
         "[0:v]split=2[a][b];[a]scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,gblur=sigma=40,eq=brightness=-0.10:saturation=1.05[bg];"
         "[b]scale=%d:-2:force_original_aspect_ratio=decrease,eq=contrast=1.05:saturation=1.08[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2[v]" % fgw,
         "-map", "[v]", still])
    fc = ("[0:v]zoompan=z='%s':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30[zp];"
          "[1:v]%s[cap];[zp][cap]overlay=0:0,format=yuv420p[v]" % (z, CAP_FADE))
    run(["-framerate", "30", "-loop", "1", "-t", str(dur), "-i", still,
         "-framerate", "30", "-loop", "1", "-t", str(dur), "-i", overlay,
         "-filter_complex", fc, "-map", "[v]", "-r", "30", "-c:v", "libx264", "-preset", "slow", "-crf", "18", out])

def seg_video(vid, overlay, ss, dur, out):
    fc = ("[0:v]setsar=1,split=2[bg][fg];[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=28,eq=brightness=-0.10:saturation=1.05[bgb];"
          "[fg]scale=1040:-2:force_original_aspect_ratio=decrease,eq=contrast=1.06:saturation=1.09[fgs];[bgb][fgs]overlay=(W-w)/2:(H-h)/2[base];"
          "[1:v]%s[cap];[base][cap]overlay=0:0,fps=30,format=yuv420p[v]" % CAP_FADE)
    run(["-ss", str(ss), "-t", str(dur), "-i", vid, "-framerate", "30", "-loop", "1", "-t", str(dur), "-i", overlay,
         "-filter_complex", fc, "-map", "[v]", "-an", "-r", "30", "-c:v", "libx264", "-preset", "slow", "-crf", "18", out])

def seg_card(png, dur, out, zoom=False):
    if zoom:
        still = out + ".2x.png"
        run(["-i", png, "-frames:v", "1", "-filter_complex", "[0:v]scale=2160:3840[v]", "-map", "[v]", still])
        run(["-framerate", "30", "-loop", "1", "-t", str(dur), "-i", still, "-filter_complex",
             "[0:v]zoompan=z='1+0.05*on/%d':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,format=yuv420p[v]" % max(2, int(dur*30)),
             "-map", "[v]", "-r", "30", "-c:v", "libx264", "-preset", "slow", "-crf", "18", out])
    else:
        run(["-framerate", "30", "-loop", "1", "-t", str(dur), "-i", png, "-filter_complex",
             "[0:v]scale=1080:1920,format=yuv420p[v]", "-map", "[v]", "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "19", out])

def music_bed(total, mood, out):
    if mood == "calm":
        fr, trem, lp, vol = [110, 164.81, 220, 277.18], "tremolo=f=0.15:d=0.5", 1400, 0.16
    else:
        fr, trem, lp, vol = [130.81, 164.81, 196.0, 261.63], "tremolo=f=2.0:d=0.6", 1900, 0.2
    ins = []
    for f in fr: ins += ["-f", "lavfi", "-i", "sine=frequency=%s:duration=%.2f" % (f, total+0.3)]
    run(ins + ["-filter_complex",
        "[0:a][1:a][2:a][3:a]amix=inputs=4:duration=longest,%s,lowpass=f=%d,aecho=0.8:0.7:55:0.25,volume=%s,"
        "afade=t=in:st=0:d=1,afade=t=out:st=%.2f:d=2[a]" % (trem, lp, vol, max(0.1, total-1.8)),
        "-map", "[a]", "-c:a", "pcm_s16le", out])

TRANS = ["fade", "slideleft", "slideright", "dissolve", "slideup", "smoothleft", "fade", "slideright"]

# ---------- Body & Assemble ----------
def build_body(items, cfg, wd, accent, badge):
    segs, durs = [], []
    for i, it in enumerate(items):
        ov = os.path.join(wd, "ov_%d.png" % i)
        ov_caption(cfg.get("brand", "LUXESTYLE"), it.get("title", ""), it.get("sub", ""), accent, ov, badge)
        o = os.path.join(wd, "seg_%d.mp4" % i)
        if it.get("type") == "video":
            seg_video(fetch(it["src"], wd), ov, float(it.get("ss", 0)), float(it.get("dur", 1.8)), o)
        else:
            seg_image(fetch(it["src"], wd), ov, float(it.get("dur", 1.8)), it.get("zoom", "in") == "in", o, int(it.get("fgw", 1720)))
        segs.append(o); durs.append(float(it.get("dur", 1.8))); print("  item %d ok (%s)" % (i+1, it.get("title", "")))
    sp = cfg.get("socialproof")
    if sp:
        png = os.path.join(wd, "proof.png")
        card_proof(sp.get("stars", 5), sp.get("title", "Über 50 Bewertungen"), sp.get("sub", "Versand aus der Schweiz"),
                   sp.get("foot", ""), accent, png)
        o = os.path.join(wd, "proof.mp4"); seg_card(png, float(sp.get("dur", 1.8)), o, zoom=True)
        segs.append(o); durs.append(float(sp.get("dur", 1.8))); print("  social-proof ok")
    ep = os.path.join(wd, "end.png"); card_end(cfg.get("brand", "LUXESTYLE"), cfg.get("code", "WELCOME10"),
                                               cfg.get("domain", "luxestyle.ch"), accent, ep)
    eo = os.path.join(wd, "end.mp4"); ed = float(cfg.get("endcard_dur", 2.6)); seg_card(ep, ed, eo)
    segs.append(eo); durs.append(ed)
    return segs, durs

def synth_voice(text, out_wav, model_path=None):
    """Gratis deutsche Stimme via piper-tts (lokal, kein API). Gibt True/False."""
    try:
        import wave
        from piper import PiperVoice
    except Exception:
        sys.stderr.write("  ! Voiceover übersprungen: piper-tts fehlt (pip install piper-tts).\n"); return False
    model = model_path or os.environ.get("LUXE_PIPER_VOICE")
    if not model:
        import glob
        cands = []
        for d in (os.path.dirname(os.path.abspath(__file__)), "/tmp/piper_voice", os.getcwd()):
            cands += sorted(glob.glob(os.path.join(d, "*.onnx")))
        model = cands[0] if cands else None
    if not (model and os.path.exists(model)):
        sys.stderr.write("  ! Voiceover übersprungen: keine piper-Stimme (.onnx). Setze LUXE_PIPER_VOICE oder 'voice_model'.\n"); return False
    try:
        v = PiperVoice.load(model)
        with wave.open(out_wav, "wb") as wf:
            v.synthesize_wav(text, wf)
        return os.path.exists(out_wav)
    except Exception as e:
        sys.stderr.write("  ! Voiceover-Fehler: %s\n" % e); return False

def assemble(hook_seg, hook_dur, body_segs, body_durs, cfg, accent, out_path):
    segs = ([hook_seg] if hook_seg else []) + body_segs
    durs = ([hook_dur] if hook_seg else []) + body_durs
    T = float(cfg.get("transition", 0.3))
    inp = []
    for s in segs: inp += ["-i", s]
    fc, prev, total = [], "[0:v]", durs[0]
    for i in range(1, len(segs)):
        tr = TRANS[(i-1) % len(TRANS)]; lbl = "[x%d]" % i
        fc.append("%s[%d:v]xfade=transition=%s:duration=%.2f:offset=%.2f%s" % (prev, i, tr, T, total-T, lbl))
        prev = lbl; total += durs[i] - T
    wd = os.path.dirname(out_path) or "."
    montage = os.path.join(tempfile.gettempdir(), "montage_%d.mp4" % (abs(hash(out_path)) % 99999))
    run(inp + ["-filter_complex", ";".join(fc), "-map", prev, "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "18", montage])
    mood = cfg.get("music", "upbeat"); mood = "upbeat" if mood is True else mood
    progress = bool(cfg.get("progress_bar", True)) and HAS_DRAWBOX
    ac = "0x%02X%02X%02X" % accent
    vchain = "[0:v]setsar=1"
    if progress: vchain += ",drawbox=x=0:y=0:w='iw*min(t/%.2f\\,1)':h=10:color=%s@0.9:t=fill" % (total, ac)
    vchain += ",format=yuv420p[v]"

    # Optional gratis Voiceover (piper) + Musik-Bed; Musik wird unter der Stimme geduckt
    vo = None
    if cfg.get("voiceover"):
        vo = montage + ".vo.wav"
        if not synth_voice(cfg["voiceover"], vo, cfg.get("voice_model")): vo = None
    mus = None
    if mood:
        mus = montage + ".mus.wav"; music_bed(total, mood, mus)

    enc = ["-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    ins = ["-i", montage]
    if mus: ins += ["-i", mus]
    if vo:  ins += ["-i", vo]
    if mus and vo:
        af = vchain + ";[1:a]volume=0.4[m];[2:a]volume=1.0[v2];[m][v2]amix=inputs=2:duration=first:normalize=0[a]"
        run(ins + ["-filter_complex", af, "-map", "[v]", "-map", "[a]", *enc, "-c:a", "aac", "-b:a", "192k", "-shortest", out_path])
    elif vo:
        run(ins + ["-filter_complex", vchain, "-map", "[v]", "-map", "1:a", *enc, "-c:a", "aac", "-b:a", "192k", "-shortest", out_path])
    elif mus:
        run(ins + ["-filter_complex", vchain, "-map", "[v]", "-map", "1:a", *enc, "-c:a", "aac", "-b:a", "192k", "-shortest", out_path])
    else:
        run(ins + ["-filter_complex", vchain, "-map", "[v]", "-r", "30", *enc, out_path])
    return total

def norm_hook(h):
    if isinstance(h, str):
        parts = h.split("|", 1); return {"title": parts[0].strip(), "sub": (parts[1].strip() if len(parts) > 1 else "")}
    return dict(h)

def build(cfg, out_path):
    accent = hexrgb(cfg.get("accent")); badge = bool(cfg.get("price_badge", False))
    wd = tempfile.mkdtemp(prefix="luxe_reel_")
    items = cfg.get("items")
    if not items and cfg.get("shopify"):
        items, warns = shopify_resolve(cfg["shopify"])
        for w in warns: print("  ! " + w)
        if not items: sys.exit("Shopify: keine passenden (published) Produkte gefunden.")
        print("  Shopify-Auto: %d Produkte geladen" % len(items))
    if not items: sys.exit("Konfig braucht 'items' ODER 'shopify'.")

    body_segs, body_durs = build_body(items, cfg, wd, accent, badge)

    hooks = cfg.get("hooks")
    if not hooks: hooks = [cfg["hook"]] if cfg.get("hook") else [None]
    hook_default_src = cfg.get("hook_src") or (items[0]["src"] if items else None)
    multi = len([h for h in hooks if h]) > 1
    base, ext = os.path.splitext(out_path); letters = "ABCDEFGH"
    outs = []
    for i, hk in enumerate(hooks):
        hseg = hdur = None
        if hk:
            hk = norm_hook(hk); src = hk.get("src") or hook_default_src
            ov = os.path.join(wd, "hook_%d.png" % i)
            ov_hook(cfg.get("brand", "LUXESTYLE"), hk.get("title", "SOMMER-SALE"),
                    hk.get("sub", "-10% mit Code " + cfg.get("code", "WELCOME10")), accent, ov)
            hseg = os.path.join(wd, "hookseg_%d.mp4" % i); hdur = float(hk.get("dur", 2.0))
            seg_image(fetch(src, wd), ov, hdur, True, hseg, int(hk.get("fgw", 1720)))
        oi = "%s_%s%s" % (base, letters[i], ext) if multi else out_path
        tot = assemble(hseg, hdur, body_segs, body_durs, cfg, accent, oi)
        outs.append((oi, tot)); print("OUTPUT -> %s (%.1fs)" % (oi, tot))
    return outs

def main():
    ap = argparse.ArgumentParser(description="LuxeStyle Reel-/Ad-Builder (TikTok-Premium, v3)")
    ap.add_argument("manifest", nargs="?", help="JSON-Konfig")
    ap.add_argument("--out", default=None)
    ap.add_argument("--shopify", help="Komma-getrennte Produkt-Handles (Auto-Modus, braucht ENV)")
    ap.add_argument("--shopify-query", help="Shopify-Filter statt Handles, z.B. 'tag:sommer-2026 AND status:active'")
    ap.add_argument("--limit", type=int, default=8)
    a = ap.parse_args()
    if a.manifest:
        cfg = json.load(open(a.manifest, encoding="utf-8"))
    else:
        cfg = {}
    if a.shopify or a.shopify_query:
        sp = cfg.get("shopify", {})
        if a.shopify: sp["handles"] = [h.strip() for h in a.shopify.split(",") if h.strip()]
        if a.shopify_query: sp["query"] = a.shopify_query
        sp.setdefault("limit", a.limit); cfg["shopify"] = sp
        cfg.setdefault("socialproof", {"stars": 5, "title": "Über 50 Bewertungen",
                                       "sub": "Versand aus der Schweiz", "foot": "wasserfest · anlauffrei · hypoallergen"})
        cfg.setdefault("hook", {"title": "SOMMER-SALE", "sub": "-10% mit Code WELCOME10"})
        cfg.setdefault("price_badge", True)
    if not cfg.get("items") and not cfg.get("shopify"):
        sys.exit("Bitte manifest.json ODER --shopify/--shopify-query angeben.")
    out = a.out or cfg.get("out", "luxestyle_reel.mp4")
    nh = len([h for h in (cfg.get("hooks") or []) if h])
    print("Baue %s%s%s -> %s" % (
        ("Shopify-Auto" if cfg.get("shopify") and not cfg.get("items") else "%d Items" % len(cfg.get("items", []))),
        ", +hook" if (cfg.get("hook") or cfg.get("hooks")) else "",
        " (A/B: %d Varianten)" % nh if nh > 1 else "", out))
    build(cfg, out)

if __name__ == "__main__":
    main()
