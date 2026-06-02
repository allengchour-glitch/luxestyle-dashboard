#!/usr/bin/env python3
"""
LuxeStyle Reel-/Ad-Builder  —  TikTok-Premium Automatisierungs-Tool (v2)

Baut aus einer JSON-Konfig automatisch ein fertiges, gebrandetes 9:16-Reel/Ad
im TikTok-Premium-Stil:
  • Blur-Fill-Hintergrund (jedes Format -> 1080x1920)
  • Branding + Caption in TikTok-Safe-Zone, Captions blenden animiert ein
  • flüssiger, jitterfreier Ken-Burns-Zoom (2x-Auflösung, linear, alternierend)
  • optionale Hook-Karte (Auto-Opener) + Social-Proof-Karte (gezeichnete Sterne)
  • Story-Progress-Bar oben, Premium-Transitions-Mix
  • Musik-Moods (calm/upbeat, lizenzfrei) + konfigurierbare Markenfarbe
  • CTA-End-Card; Export 1080x1920 H.264 yuv420p +faststart (TikTok/IG/YT-ready)

Nutzung:
    python3 build_reel.py manifest.json [--out out.mp4]

Abhängigkeiten: Pillow, imageio-ffmpeg  (pip install Pillow imageio-ffmpeg)
"""
import json, os, sys, math, tempfile, subprocess, urllib.request, argparse

# ---------- ffmpeg + Fonts ----------
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
    os.path.join(_WIN, "Fonts", "arialbd.ttf"),
    os.path.join(_WIN, "Fonts", "segoeuib.ttf"),
    os.path.join(_WIN, "Fonts", "arial.ttf"),
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial.ttf",
])
if not FONT:
    sys.exit("Keine TTF-Font gefunden. Setze LUXE_FONT=...\\arialbd.ttf oder installiere DejaVu/Liberation.")

FF = find_ffmpeg()
W, H = 1080, 1920

def has_filter(name):
    try:
        out = subprocess.run([FF, "-hide_banner", "-filters"], capture_output=True, text=True).stdout
        return (" %s " % name) in out
    except Exception:
        return False
HAS_DRAWBOX = has_filter("drawbox")

def run(args):
    r = subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", *args],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-2000:] + "\n"); raise SystemExit("ffmpeg-Fehler")

def fetch(src, wd):
    if src.startswith(("http://", "https://")):
        ext = os.path.splitext(src.split("?")[0])[1] or ".img"
        dst = os.path.join(wd, "src_%d%s" % (abs(hash(src)) % 99999, ext))
        urllib.request.urlretrieve(src, dst); return dst
    if not os.path.exists(src): raise SystemExit("Datei fehlt: " + src)
    return src

def hexrgb(s, default=(201, 162, 75)):
    if not s: return default
    s = s.lstrip("#")
    try: return tuple(int(s[i:i+2], 16) for i in (0, 2, 4))
    except Exception: return default

# ---------- PIL Overlays ----------
def _pil():
    from PIL import Image, ImageDraw, ImageFont
    return Image, ImageDraw, ImageFont

def _cx(d, t, f):
    b = d.textbbox((0, 0), t, font=f); return (W - (b[2] - b[0])) // 2 - b[0]
def _sh(d, xy, t, f, fill, off=2, sh=(0, 0, 0, 170)):
    x, y = xy; d.text((x+off, y+off), t, font=f, fill=sh); d.text((x, y), t, font=f, fill=fill)
def _star(d, cxp, cyp, R, fill):
    r = R*0.42; pts = []
    for i in range(10):
        a = -math.pi/2 + i*math.pi/5; rad = R if i % 2 == 0 else r
        pts.append((cxp+rad*math.cos(a), cyp+rad*math.sin(a)))
    d.polygon(pts, fill=fill)

def ov_caption(brand, l1, l2, accent, out, badge=False):
    Image, ImageDraw, ImageFont = _pil()
    GOLD = accent + (255,)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    fw = ImageFont.truetype(FONT, 56); f1 = ImageFont.truetype(FONT, 50); f2 = ImageFont.truetype(FONT, 34)
    wm = " ".join(brand.upper())
    _sh(d, (_cx(d, wm, fw), 96), wm, fw, (255, 255, 255, 240))
    yL = 1150
    d.rectangle([(W-200)//2, yL, (W+200)//2, yL+4], fill=GOLD)
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
    Image, ImageDraw, ImageFont = _pil()
    GOLD = accent + (255,)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rectangle([0, 150, W, 650], fill=(15, 12, 10, 140))
    fw = ImageFont.truetype(FONT, 46); ft = ImageFont.truetype(FONT, 116); fs = ImageFont.truetype(FONT, 48)
    wm = " ".join(brand.upper())
    _sh(d, (_cx(d, wm, fw), 190), wm, fw, (255, 255, 255, 235))
    _sh(d, (_cx(d, title, ft), 300), title, ft, (255, 255, 255, 255), off=3)
    d.rectangle([(W-300)//2, 470, (W+300)//2, 476], fill=GOLD)
    if sub: _sh(d, (_cx(d, sub, fs), 502), sub, fs, GOLD)
    img.save(out)

def card_proof(stars, title, sub, foot, accent, out):
    Image, ImageDraw, ImageFont = _pil()
    GOLD = accent + (255,)
    ec = Image.new("RGB", (W, H), (17, 15, 14)); d = ImageDraw.Draw(ec)
    n = max(1, min(5, int(stars))); R = 46; gap = 120; cyp = 600
    sx = W//2 - (n-1)*gap//2
    for i in range(n): _star(d, sx+i*gap, cyp, R, accent)
    f1 = ImageFont.truetype(FONT, 56); f2 = ImageFont.truetype(FONT, 40); f3 = ImageFont.truetype(FONT, 34)
    if title: _sh(d, (_cx(d, title, f1), 700), title, f1, (255, 255, 255))
    if sub:   _sh(d, (_cx(d, sub, f2), 790), sub, f2, (220, 220, 220))
    d.rectangle([(W-260)//2, 880, (W+260)//2, 885], fill=GOLD)
    if foot:  _sh(d, (_cx(d, foot, f3), 915), foot, f3, accent)
    ec.save(out)

def card_end(brand, code, domain, accent, out):
    Image, ImageDraw, ImageFont = _pil()
    GOLD = accent + (255,)
    ec = Image.new("RGB", (W, H), (17, 15, 14)); d = ImageDraw.Draw(ec)
    fb = ImageFont.truetype(FONT, 92); f1 = ImageFont.truetype(FONT, 50); f2 = ImageFont.truetype(FONT, 38)
    wm = " ".join(brand.upper())
    _sh(d, (_cx(d, wm, fb), 700), wm, fb, (255, 255, 255), off=3, sh=(0, 0, 0, 150))
    d.rectangle([(W-260)//2, 852, (W+260)//2, 857], fill=GOLD)
    if code:
        t = "Code %s = 10%%" % code; _sh(d, (_cx(d, t, f1), 900), t, f1, accent)
    t = "Jetzt shoppen -> %s" % domain; _sh(d, (_cx(d, t, f2), 990), t, f2, (225, 225, 225))
    ec.save(out)

# ---------- Segmente (Caption blendet animiert ein) ----------
CAP_FADE = "fade=t=in:st=0.05:d=0.45:alpha=1"

def seg_image(img, overlay, dur, zoom_in, out, fgw=1720):
    n = max(2, int(dur*30))
    z = "1+0.07*on/%d" % n if zoom_in else "1.07-0.07*on/%d" % n
    still = out + ".png"
    fc1 = ("[0:v]split=2[a][b];"
           "[a]scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,gblur=sigma=40,eq=brightness=-0.10:saturation=1.05[bg];"
           "[b]scale=%d:-2:force_original_aspect_ratio=decrease,eq=contrast=1.05:saturation=1.08[fg];"
           "[bg][fg]overlay=(W-w)/2:(H-h)/2[v]" % fgw)
    run(["-i", img, "-frames:v", "1", "-filter_complex", fc1, "-map", "[v]", still])
    fc2 = ("[0:v]zoompan=z='%s':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30[zp];"
           "[1:v]%s[cap];[zp][cap]overlay=0:0,format=yuv420p[v]" % (z, CAP_FADE))
    run(["-framerate", "30", "-loop", "1", "-t", str(dur), "-i", still,
         "-framerate", "30", "-loop", "1", "-t", str(dur), "-i", overlay,
         "-filter_complex", fc2, "-map", "[v]", "-r", "30", "-c:v", "libx264", "-preset", "slow", "-crf", "18", out])

def seg_video(vid, overlay, ss, dur, out):
    fc = ("[0:v]setsar=1,split=2[bg][fg];"
          "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=28,eq=brightness=-0.10:saturation=1.05[bgb];"
          "[fg]scale=1040:-2:force_original_aspect_ratio=decrease,eq=contrast=1.06:saturation=1.09[fgs];"
          "[bgb][fgs]overlay=(W-w)/2:(H-h)/2[base];"
          "[1:v]%s[cap];[base][cap]overlay=0:0,fps=30,format=yuv420p[v]" % CAP_FADE)
    run(["-ss", str(ss), "-t", str(dur), "-i", vid,
         "-framerate", "30", "-loop", "1", "-t", str(dur), "-i", overlay,
         "-filter_complex", fc, "-map", "[v]", "-an", "-r", "30", "-c:v", "libx264", "-preset", "slow", "-crf", "18", out])

def seg_card(png, dur, out, zoom=False):
    if zoom:
        still = out+".2x.png"
        run(["-i", png, "-frames:v", "1", "-filter_complex", "[0:v]scale=2160:3840[v]", "-map", "[v]", still])
        fc = "[0:v]zoompan=z='1+0.05*on/%d':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,format=yuv420p[v]" % max(2, int(dur*30))
        run(["-framerate", "30", "-loop", "1", "-t", str(dur), "-i", still, "-filter_complex", fc,
             "-map", "[v]", "-r", "30", "-c:v", "libx264", "-preset", "slow", "-crf", "18", out])
    else:
        run(["-framerate", "30", "-loop", "1", "-t", str(dur), "-i", png,
             "-filter_complex", "[0:v]scale=1080:1920,format=yuv420p[v]", "-map", "[v]",
             "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "19", out])

def music_bed(total, mood, out):
    if mood == "calm":
        freqs = [110, 164.81, 220, 277.18]; trem = "tremolo=f=0.15:d=0.5"; lp = 1400; vol = 0.16
    else:  # upbeat
        freqs = [130.81, 164.81, 196.0, 261.63]; trem = "tremolo=f=2.0:d=0.6"; lp = 1900; vol = 0.2
    ins = []
    for f in freqs: ins += ["-f", "lavfi", "-i", "sine=frequency=%s:duration=%.2f" % (f, total+0.3)]
    fc = ("[0:a][1:a][2:a][3:a]amix=inputs=4:duration=longest,%s,lowpass=f=%d,"
          "aecho=0.8:0.7:55:0.25,volume=%s,afade=t=in:st=0:d=1,afade=t=out:st=%.2f:d=2[a]"
          % (trem, lp, vol, max(0.1, total-1.8)))
    run(ins + ["-filter_complex", fc, "-map", "[a]", "-c:a", "pcm_s16le", out])

TRANS = ["fade", "slideleft", "slideright", "dissolve", "slideup", "smoothleft", "fade", "slideright"]

def build(cfg, out_path):
    brand  = cfg.get("brand", "LUXESTYLE"); code = cfg.get("code", "WELCOME10")
    domain = cfg.get("domain", "luxestyle.ch"); T = float(cfg.get("transition", 0.3))
    accent = hexrgb(cfg.get("accent"))
    mood   = cfg.get("music", "upbeat");  mood = "upbeat" if mood is True else mood
    badge  = bool(cfg.get("price_badge", False))
    progress = bool(cfg.get("progress_bar", True)) and HAS_DRAWBOX
    wd = tempfile.mkdtemp(prefix="luxe_reel_"); segs, durs = [], []

    # Hook (optional)
    hk = cfg.get("hook")
    if hk:
        ov = os.path.join(wd, "hook.png"); ov_hook(brand, hk.get("title", "SOMMER-SALE"),
                                                   hk.get("sub", "-10% mit Code "+code), accent, ov)
        o = os.path.join(wd, "s_hook.mp4"); dur = float(hk.get("dur", 2.0))
        seg_image(fetch(hk["src"], wd), ov, dur, True, o, int(hk.get("fgw", 1720)))
        segs.append(o); durs.append(dur); print("  hook ok (%ss)" % dur)

    # Items
    for i, it in enumerate(cfg["items"]):
        dur = float(it.get("dur", 1.8))
        ov = os.path.join(wd, "ov_%d.png" % i)
        ov_caption(brand, it.get("title", ""), it.get("sub", ""), accent, ov, badge)
        o = os.path.join(wd, "seg_%d.mp4" % i)
        if it.get("type") == "video":
            seg_video(fetch(it["src"], wd), ov, float(it.get("ss", 0)), dur, o)
        else:
            seg_image(fetch(it["src"], wd), ov, dur, it.get("zoom", "in") == "in", o, int(it.get("fgw", 1720)))
        segs.append(o); durs.append(dur); print("  segment %d ok (%ss)" % (i+1, dur))

    # Social proof (optional, vor End-Card)
    sp = cfg.get("socialproof")
    if sp:
        png = os.path.join(wd, "proof.png")
        card_proof(sp.get("stars", 5), sp.get("title", "Über 50 Bewertungen"),
                   sp.get("sub", "Versand aus der Schweiz"), sp.get("foot", ""), accent, png)
        o = os.path.join(wd, "s_proof.mp4"); dur = float(sp.get("dur", 1.8))
        seg_card(png, dur, o, zoom=True); segs.append(o); durs.append(dur); print("  social-proof ok")

    # End-Card
    ep = os.path.join(wd, "end.png"); card_end(brand, code, domain, accent, ep)
    eo = os.path.join(wd, "end.mp4"); ed = float(cfg.get("endcard_dur", 2.6))
    seg_card(ep, ed, eo); segs.append(eo); durs.append(ed)

    # xfade-Kette
    inp = []
    for s in segs: inp += ["-i", s]
    fc, prev, total = [], "[0:v]", durs[0]
    for i in range(1, len(segs)):
        tr = TRANS[(i-1) % len(TRANS)]; lbl = "[x%d]" % i
        fc.append("%s[%d:v]xfade=transition=%s:duration=%.2f:offset=%.2f%s" % (prev, i, tr, T, total-T, lbl))
        prev = lbl; total += durs[i] - T
    montage = os.path.join(wd, "montage.mp4")
    run(inp + ["-filter_complex", ";".join(fc), "-map", prev, "-r", "30",
               "-c:v", "libx264", "-preset", "medium", "-crf", "18", montage])

    # Finale: optional Story-Progress-Bar + Musik
    ac = "0x%02X%02X%02X" % accent
    vchain = "[0:v]setsar=1"
    if progress:
        vchain += (",drawbox=x=0:y=0:w='iw*min(t/%.2f\\,1)':h=10:color=%s@0.9:t=fill" % (total, ac))
    vchain += ",format=yuv420p[v]"
    if mood:
        mus = os.path.join(wd, "music.wav"); music_bed(total, mood, mus)
        run(["-i", montage, "-i", mus, "-filter_complex", vchain, "-map", "[v]", "-map", "1:a",
             "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
             "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-shortest", out_path])
    else:
        run(["-i", montage, "-filter_complex", vchain, "-map", "[v]", "-r", "30",
             "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
             "-movflags", "+faststart", out_path])
    print("FERTIG -> %s (%.1fs%s)" % (out_path, total, ", progress-bar" if progress else ""))

def main():
    ap = argparse.ArgumentParser(description="LuxeStyle Reel-/Ad-Builder (TikTok-Premium)")
    ap.add_argument("manifest"); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    cfg = json.load(open(a.manifest, encoding="utf-8"))
    out = a.out or cfg.get("out", "luxestyle_reel.mp4")
    print("Baue Reel (%d Items%s%s) -> %s" % (
        len(cfg["items"]), ", +hook" if cfg.get("hook") else "",
        ", +proof" if cfg.get("socialproof") else "", out))
    build(cfg, out)

if __name__ == "__main__":
    main()
