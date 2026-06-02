#!/usr/bin/env python3
"""
LuxeStyle Reel-/Ad-Builder  —  Automatisierungs-Tool

Baut aus einer JSON-Konfig automatisch ein fertiges, gebrandetes 9:16-Reel/Ad
(Blur-Fill-Hintergrund, LUXESTYLE-Branding + Captions in TikTok-Safe-Zone,
flüssiger Ken-Burns-Zoom, abwechselnde Transitions, lizenzfreier Musik-Bed,
CTA-End-Card). Output: TikTok/IG/YT-ready (1080x1920, yuv420p, +faststart).

Kapselt die in `reel-build-recipe-ffmpeg.md` dokumentierte Pipeline.

Nutzung:
    python3 build_reel.py manifest.json
    python3 build_reel.py manifest.json --out mein_reel.mp4

Abhängigkeiten: Pillow, imageio-ffmpeg  (pip install Pillow imageio-ffmpeg)
Kein Netzwerk nötig für lokale Bilder; http(s)-URLs werden automatisch geladen.
"""
import json, os, sys, math, tempfile, subprocess, urllib.request, argparse

# ---------- Umgebung: ffmpeg + Fonts auflösen ----------
def find_ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        from shutil import which
        exe = which("ffmpeg")
        if exe: return exe
        sys.exit("ffmpeg nicht gefunden – `pip install imageio-ffmpeg` oder ffmpeg installieren.")

def first_existing(paths):
    for p in paths:
        if p and os.path.exists(p): return p
    return None

WORDMARK_FONT = first_existing([
    "/mnt/skills/examples/canvas-design/canvas-fonts/BigShoulders-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
])
BODY_FONT = first_existing([
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/mnt/skills/examples/canvas-design/canvas-fonts/BigShoulders-Bold.ttf",
])
if not (WORDMARK_FONT and BODY_FONT):
    sys.exit("Keine TTF-Font gefunden (Liberation/DejaVu installieren).")

FF = find_ffmpeg()
W, H = 1080, 1920
GOLD = (201, 162, 75, 255)

def run(args):
    r = subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", *args],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-2000:] + "\n"); raise SystemExit("ffmpeg-Fehler")

def fetch(src, workdir):
    """Lokaler Pfad oder URL -> lokaler Pfad."""
    if src.startswith(("http://", "https://")):
        ext = os.path.splitext(src.split("?")[0])[1] or ".img"
        dst = os.path.join(workdir, "src_%d%s" % (abs(hash(src)) % 99999, ext))
        urllib.request.urlretrieve(src, dst)
        return dst
    if not os.path.exists(src): raise SystemExit("Datei fehlt: " + src)
    return src

# ---------- Text-Overlays (PIL, da ffmpeg-Static oft kein drawtext hat) ----------
def make_overlay(brand, line1, line2, out_png):
    from PIL import Image, ImageDraw, ImageFont
    def fnt(path, sz): return ImageFont.truetype(path, sz)
    def cx(d, t, f):
        b = d.textbbox((0, 0), t, font=f); return (W - (b[2] - b[0])) // 2 - b[0]
    def shadow(d, xy, t, f, fill, off=2):
        x, y = xy
        d.text((x + off, y + off), t, font=f, fill=(0, 0, 0, 170))
        d.text((x, y), t, font=f, fill=fill)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    wm = " ".join(brand.upper())
    shadow(d, (cx(d, wm, fnt(WORDMARK_FONT, 56)), 96), wm, fnt(WORDMARK_FONT, 56), (255, 255, 255, 240))
    # Caption mittig-unten (über TikTok-CTA-Zone, weg von rechten Icons)
    yL = 1150
    d.rectangle([(W - 200) // 2, yL, (W + 200) // 2, yL + 4], fill=GOLD)
    if line1: shadow(d, (cx(d, line1, fnt(BODY_FONT, 50)), yL + 22), line1, fnt(BODY_FONT, 50), (255, 255, 255, 255))
    if line2: shadow(d, (cx(d, line2, fnt(BODY_FONT, 34)), yL + 86), line2, fnt(BODY_FONT, 34), GOLD)
    img.save(out_png)

def make_endcard(brand, code, domain, out_png):
    from PIL import Image, ImageDraw, ImageFont
    def fnt(p, s): return ImageFont.truetype(p, s)
    def cx(d, t, f):
        b = d.textbbox((0, 0), t, font=f); return (W - (b[2] - b[0])) // 2 - b[0]
    def shadow(d, xy, t, f, fill, off=2):
        x, y = xy; d.text((x + off, y + off), t, font=f, fill=(0, 0, 0, 150)); d.text((x, y), t, font=f, fill=fill)
    ec = Image.new("RGB", (W, H), (17, 15, 14)); d = ImageDraw.Draw(ec)
    wm = " ".join(brand.upper())
    shadow(d, (cx(d, wm, fnt(WORDMARK_FONT, 92)), 700), wm, fnt(WORDMARK_FONT, 92), (255, 255, 255))
    d.rectangle([(W - 260) // 2, 852, (W + 260) // 2, 857], fill=GOLD)
    if code:
        t = "Code %s = 10%%" % code
        shadow(d, (cx(d, t, fnt(BODY_FONT, 50)), 900), t, fnt(BODY_FONT, 50), GOLD[:3])
    t = "Jetzt shoppen -> %s" % domain
    shadow(d, (cx(d, t, fnt(BODY_FONT, 38)), 990), t, fnt(BODY_FONT, 38), (225, 225, 225))
    ec.save(out_png)

# ---------- Segmente ----------
def seg_image(img, overlay, dur, zoom_in, out, fgw=1720):
    """Standbild -> Blur-Fill 9:16 + Caption + flüssiger linearer Ken-Burns."""
    n = max(2, int(dur * 30))
    z = "1+0.07*on/%d" % n if zoom_in else "1.07-0.07*on/%d" % n
    still = out + ".png"
    fc = ("[0:v]split=2[a][b];"
          "[a]scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,gblur=sigma=40,eq=brightness=-0.10:saturation=1.05[bg];"
          "[b]scale=%d:-2:force_original_aspect_ratio=decrease,eq=contrast=1.05:saturation=1.08[fg];"
          "[bg][fg]overlay=(W-w)/2:(H-h)/2[c];[1:v]scale=2160:3840[cap];[c][cap]overlay=0:0[v]" % fgw)
    run(["-i", img, "-i", overlay, "-frames:v", "1", "-filter_complex", fc, "-map", "[v]", still])
    zp = ("[0:v]zoompan=z='%s':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,format=yuv420p[v]" % z)
    run(["-framerate", "30", "-loop", "1", "-t", str(dur), "-i", still,
         "-filter_complex", zp, "-map", "[v]", "-r", "30", "-c:v", "libx264", "-preset", "slow", "-crf", "18", out])

def seg_video(vid, overlay, ss, dur, out):
    """Video-Clip -> Blur-Fill 9:16 + Caption."""
    fc = ("[0:v]setsar=1,split=2[bg][fg];"
          "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=28,eq=brightness=-0.10:saturation=1.05[bgb];"
          "[fg]scale=1040:-2:force_original_aspect_ratio=decrease,eq=contrast=1.06:saturation=1.09[fgs];"
          "[bgb][fgs]overlay=(W-w)/2:(H-h)/2[base];[base][1:v]overlay=0:0,fps=30,format=yuv420p[v]")
    run(["-ss", str(ss), "-t", str(dur), "-i", vid, "-i", overlay, "-filter_complex", fc,
         "-map", "[v]", "-an", "-r", "30", "-c:v", "libx264", "-preset", "slow", "-crf", "18", out])

def seg_card(png, dur, out):
    run(["-framerate", "30", "-loop", "1", "-t", str(dur), "-i", png,
         "-filter_complex", "[0:v]scale=1080:1920,format=yuv420p[v]", "-map", "[v]",
         "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "19", out])

def music_bed(total, out):
    freqs = [130.81, 164.81, 196.0, 261.63]  # C-Dur-Pad, hell
    ins = []
    for f in freqs: ins += ["-f", "lavfi", "-i", "sine=frequency=%s:duration=%.2f" % (f, total + 0.3)]
    fc = ("[0:a][1:a][2:a][3:a]amix=inputs=4:duration=longest,tremolo=f=2.0:d=0.6,"
          "lowpass=f=1900,aecho=0.8:0.7:55:0.25,volume=0.2,"
          "afade=t=in:st=0:d=1,afade=t=out:st=%.2f:d=2[a]" % max(0.1, total - 1.8))
    run(ins + ["-filter_complex", fc, "-map", "[a]", "-c:a", "pcm_s16le", out])

# ---------- Hauptablauf ----------
TRANS = ["fade", "slideleft", "slideright", "fade", "slideup", "slideleft", "fade", "slideright"]

def build(cfg, out_path):
    brand  = cfg.get("brand", "LUXESTYLE")
    code   = cfg.get("code", "WELCOME10")
    domain = cfg.get("domain", "luxestyle.ch")
    T      = float(cfg.get("transition", 0.3))
    wd = tempfile.mkdtemp(prefix="luxe_reel_")
    segs, durs = [], []

    for i, it in enumerate(cfg["items"]):
        dur = float(it.get("dur", 1.8))
        ov = os.path.join(wd, "ov_%d.png" % i)
        make_overlay(brand, it.get("title", ""), it.get("sub", ""), ov)
        out = os.path.join(wd, "seg_%d.mp4" % i)
        if it.get("type") == "video":
            seg_video(fetch(it["src"], wd), ov, float(it.get("ss", 0)), dur, out)
        else:
            seg_image(fetch(it["src"], wd), ov, dur, it.get("zoom", "in") == "in", out,
                      int(it.get("fgw", 1720)))
        segs.append(out); durs.append(dur); print("  segment %d ok (%ss)" % (i + 1, dur))

    # End-Card
    ec_png = os.path.join(wd, "end.png"); make_endcard(brand, code, domain, ec_png)
    ec = os.path.join(wd, "end.mp4"); ecd = float(cfg.get("endcard_dur", 2.6))
    seg_card(ec_png, ecd, ec); segs.append(ec); durs.append(ecd)

    # xfade-Kette
    inputs = []
    for s in segs: inputs += ["-i", s]
    fc, prev, off, total = [], "[0:v]", 0.0, durs[0]
    for i in range(1, len(segs)):
        off = total - T
        tr = TRANS[(i - 1) % len(TRANS)]
        lbl = "[x%d]" % i
        fc.append("%s[%d:v]xfade=transition=%s:duration=%.2f:offset=%.2f%s" % (prev, i, tr, T, off, lbl))
        prev = lbl; total += durs[i] - T
    montage = os.path.join(wd, "montage.mp4")
    run(inputs + ["-filter_complex", ";".join(fc), "-map", prev, "-r", "30",
                  "-c:v", "libx264", "-preset", "medium", "-crf", "18", montage])

    # Musik + finales Encode
    if cfg.get("music", True):
        mus = os.path.join(wd, "music.wav"); music_bed(total, mus)
        run(["-i", montage, "-i", mus, "-filter_complex", "[0:v]setsar=1,format=yuv420p[v]",
             "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
             "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k",
             "-shortest", out_path])
    else:
        run(["-i", montage, "-filter_complex", "[0:v]setsar=1,format=yuv420p[v]", "-map", "[v]",
             "-r", "30", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
             "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_path])
    print("FERTIG -> %s (%.1fs)" % (out_path, total))

def main():
    ap = argparse.ArgumentParser(description="LuxeStyle Reel-/Ad-Builder")
    ap.add_argument("manifest", help="JSON-Konfig (siehe sample_reel.json)")
    ap.add_argument("--out", default=None, help="Output-MP4 (überschreibt manifest.out)")
    a = ap.parse_args()
    cfg = json.load(open(a.manifest, encoding="utf-8"))
    out = a.out or cfg.get("out", "luxestyle_reel.mp4")
    print("Baue Reel aus %d Items -> %s" % (len(cfg["items"]), out))
    build(cfg, out)

if __name__ == "__main__":
    main()
