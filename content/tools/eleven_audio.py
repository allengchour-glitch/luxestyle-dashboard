#!/usr/bin/env python3
"""
LuxeStyle ElevenLabs-Audio  —  erzeugt **KI-Stimme (TTS)** und **KI-Musik** für die
Reels. Premium-Audio statt piper/Synth; auf Paid-Plan kommerziell lizenziert (ad-safe).

Output-Dateien werden dann in build_reel.py genutzt:
  "voiceover_file": "vo.mp3"   und/oder   "music_file": "bed.mp3"

ENV (nie committen / nicht in den Chat):
  ELEVENLABS_API_KEY   (elevenlabs.io -> Profil -> API Keys)

Nutzung:
  # Stimme (deutsch) erzeugen
  python eleven_audio.py tts --text "Entdecke LuxeStyle. Sommer 2026." --out vo.mp3
  python eleven_audio.py tts --text "..." --voice <VOICE_ID> --model eleven_multilingual_v2
  # verfügbare Stimmen auflisten (Voice-IDs)
  python eleven_audio.py voices
  # Musik erzeugen (Prompt -> Track der gewünschten Länge)
  python eleven_audio.py music --prompt "upbeat premium fashion, soft beat, swiss luxury" --dur 12 --out bed.mp3

Nur Standardbibliothek (urllib). Audio kommt als MP3.
Hinweis: Credits werden verbraucht -> sparsam testen. Musik kann teurer sein als TTS.
"""
import os, sys, json, argparse, urllib.request, urllib.error

BASE = "https://api.elevenlabs.io/v1"
# Default-Stimme: vielseitig & multilingual (für DE eleven_multilingual_v2 nutzen).
DEFAULT_VOICE = "XrExE9yKIg1WjnnlVkGX"  # "Matilda" (multilingual, warm) – per --voice überschreibbar
DEFAULT_MODEL = "eleven_multilingual_v2"


def key():
    k = os.environ.get("ELEVENLABS_API_KEY")
    if not k:
        sys.exit("Bitte ELEVENLABS_API_KEY setzen (elevenlabs.io -> Profil -> API Keys). "
                 "Als ENV/Secret, NICHT im Chat.")
    return k


def _req(method, path, api_key, json_body=None, accept="application/json"):
    url = BASE + path
    headers = {"xi-api-key": api_key, "Accept": accept}
    data = None
    if json_body is not None:
        data = json.dumps(json_body).encode(); headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.read(), r.headers.get_content_type()
    except urllib.error.HTTPError as e:
        sys.exit("ElevenLabs HTTP %s: %s" % (e.code, e.read().decode()[:600]))


def list_voices(api_key):
    raw, _ = _req("GET", "/voices", api_key)
    data = json.loads(raw)
    for v in data.get("voices", []):
        labels = v.get("labels", {})
        print("  %-24s %s  [%s]" % (v.get("voice_id"), v.get("name"),
              ", ".join("%s=%s" % (k, x) for k, x in labels.items())))


def tts(api_key, text, voice, model, out):
    body = {"text": text, "model_id": model,
            "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.3}}
    audio, ctype = _req("POST", "/text-to-speech/%s" % voice, api_key, json_body=body, accept="audio/mpeg")
    with open(out, "wb") as f: f.write(audio)
    print("✓ Stimme:", out, "(%d KB)" % (len(audio)//1024))


def music(api_key, prompt, dur_s, out):
    body = {"prompt": prompt, "music_length_ms": int(float(dur_s) * 1000)}
    audio, ctype = _req("POST", "/music", api_key, json_body=body, accept="audio/mpeg")
    with open(out, "wb") as f: f.write(audio)
    print("✓ Musik:", out, "(%d KB)" % (len(audio)//1024))


def main():
    ap = argparse.ArgumentParser(description="ElevenLabs: KI-Stimme & KI-Musik für Reels")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("tts"); a.add_argument("--text", required=True)
    a.add_argument("--voice", default=DEFAULT_VOICE); a.add_argument("--model", default=DEFAULT_MODEL)
    a.add_argument("--out", default="vo.mp3")
    m = sub.add_parser("music"); m.add_argument("--prompt", required=True)
    m.add_argument("--dur", default="12"); m.add_argument("--out", default="bed.mp3")
    sub.add_parser("voices")
    args = ap.parse_args()
    api_key = key()
    if args.cmd == "tts":     tts(api_key, args.text, args.voice, args.model, args.out)
    elif args.cmd == "music": music(api_key, args.prompt, args.dur, args.out)
    elif args.cmd == "voices": list_voices(api_key)


if __name__ == "__main__":
    main()
