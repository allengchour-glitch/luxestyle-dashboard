#!/usr/bin/env python3
"""
LuxeStyle TikTok-Analyse  —  öffentliche Engagement-Daten ohne API/Login.

Zieht via yt-dlp die öffentlichen Video-Metadaten eines TikTok-Profils (default
@luxestyle.ch) oder einer expliziten URL-Liste, rechnet Engagement-Kennzahlen
aus und schreibt einen JSON-Dump + einen Markdown-Report. Damit lässt sich
sehen, welche Hooks/Hashtags/Posting-Zeiten ziehen — Input für die nächsten
Reels (build_reel.py) und den Posting-Plan (../reels-schedule.csv).

(Portiert aus dem Schwester-Repo aban-news-landing, Default auf @luxestyle.ch
angepasst. Kein API-Key, kein Login — nur öffentliche Daten.)

Nutzung
-------
  # Ganzes Profil, 30 neueste Videos (Default-User @luxestyle.ch)
  python3 tiktok_analyze.py

  # Anderer User
  python3 tiktok_analyze.py --user @anderer.shop

  # Wenn --user mit "Unable to extract secondary user ID" scheitert,
  # eine beliebige Video-URL des Users als Seed mitgeben:
  python3 tiktok_analyze.py --user @luxestyle.ch \
      --seed-video https://www.tiktok.com/@luxestyle.ch/video/7300000000000000000

  # Anzahl begrenzen / Liste analysieren / Ausgabeordner
  python3 tiktok_analyze.py --max 60
  python3 tiktok_analyze.py --urls my_urls.txt
  python3 tiktok_analyze.py --out reports/

Voraussetzung
-------------
  pip install -U yt-dlp     # oder: pipx install yt-dlp

Kein API-Key, kein Login. Nur öffentliche Daten. Wenn der TikTok-Extractor von
yt-dlp bricht (passiert — TikTok ändert die Internas alle paar Monate),
`pip install -U yt-dlp` und erneut versuchen.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any


HASHTAG_RE = re.compile(r"#(\w+)", re.UNICODE)
MENTION_RE = re.compile(r"@(\w[\w.]*)", re.UNICODE)

DEFAULT_USER = "@luxestyle.ch"


def die(msg: str, code: int = 1) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def check_yt_dlp() -> None:
    if shutil.which("yt-dlp") is None:
        die(
            "yt-dlp ist nicht installiert. Installiere es mit:\n"
            "  pip install -U yt-dlp\n"
            "oder\n"
            "  pipx install yt-dlp"
        )


def normalize_user(user: str) -> str:
    user = user.strip()
    if user.startswith("http"):
        return user.rstrip("/")
    if not user.startswith("@"):
        user = "@" + user
    return f"https://www.tiktok.com/{user}"


SECONDARY_ID_ERR = "Unable to extract secondary user ID"
INSECURE = False  # via --insecure für Sandbox-/MITM-Proxy-Umgebungen


def fetch_metadata(
    target: str, max_videos: int | None, raise_on_error: bool = False
) -> tuple[list[dict[str, Any]], str]:
    """yt-dlp einmal ausführen. Gibt (videos, stderr). Stirbt bei raise_on_error."""
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--dump-json",
        "--ignore-errors",
        "--no-warnings",
    ]
    if INSECURE:
        cmd.append("--no-check-certificate")
    if max_videos:
        cmd += ["--playlist-end", str(max_videos)]
    cmd.append(target)

    print(f"→ yt-dlp: hole Metadaten für {target} ...", file=sys.stderr)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0 and not proc.stdout.strip():
        if raise_on_error:
            die(
                f"yt-dlp fehlgeschlagen (exit {proc.returncode}). Stderr:\n{proc.stderr.strip()}"
            )
        return [], proc.stderr

    videos: list[dict[str, Any]] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            videos.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return videos, proc.stderr


def discover_channel_id(seed_video_url: str) -> str:
    """Ein Video holen und die interne channel_id (secUid) ziehen."""
    videos, _ = fetch_metadata(seed_video_url, None, raise_on_error=True)
    if not videos:
        die(f"konnte aus --seed-video kein Video extrahieren: {seed_video_url}")
    v = videos[0]
    cid = v.get("channel_id") or v.get("uploader_id")
    if not cid:
        die(
            "Seed-Video enthielt keine channel_id / uploader_id.\n"
            "Probiere eine andere Video-URL desselben Users."
        )
    print(f"→ channel_id gefunden: {cid}", file=sys.stderr)
    return cid


def slim(v: dict[str, Any]) -> dict[str, Any]:
    """yt-dlp-Video-Dict auf die relevanten Felder reduzieren."""
    desc = v.get("description") or v.get("title") or ""
    timestamp = v.get("timestamp")  # unix seconds
    upload_dt = (
        datetime.fromtimestamp(timestamp, tz=timezone.utc) if timestamp else None
    )
    views = int(v.get("view_count") or 0)
    likes = int(v.get("like_count") or 0)
    comments = int(v.get("comment_count") or 0)
    shares = int(v.get("repost_count") or v.get("share_count") or 0)
    return {
        "id": v.get("id"),
        "url": v.get("webpage_url") or v.get("url"),
        "uploader": v.get("uploader") or v.get("creator"),
        "upload_date": upload_dt.isoformat() if upload_dt else None,
        "weekday": upload_dt.strftime("%a") if upload_dt else None,
        "hour_utc": upload_dt.hour if upload_dt else None,
        "duration_s": v.get("duration"),
        "description": desc,
        "hashtags": HASHTAG_RE.findall(desc),
        "mentions": MENTION_RE.findall(desc),
        "views": views,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "engagement_rate": round((likes + comments + shares) / views, 4) if views else 0.0,
        "music": (v.get("track") or v.get("artist") or None),
    }


def analyze(videos: list[dict[str, Any]]) -> dict[str, Any]:
    if not videos:
        return {"video_count": 0}

    totals = {
        "views": sum(v["views"] for v in videos),
        "likes": sum(v["likes"] for v in videos),
        "comments": sum(v["comments"] for v in videos),
        "shares": sum(v["shares"] for v in videos),
    }
    views_series = [v["views"] for v in videos]

    # Per-Hashtag-Aggregate
    tag_stats: dict[str, dict[str, float]] = defaultdict(
        lambda: {"count": 0, "views": 0, "likes": 0, "engagement_sum": 0.0}
    )
    for v in videos:
        for tag in {t.lower() for t in v["hashtags"]}:
            s = tag_stats[tag]
            s["count"] += 1
            s["views"] += v["views"]
            s["likes"] += v["likes"]
            s["engagement_sum"] += v["engagement_rate"]

    hashtags_ranked = sorted(
        (
            {
                "tag": tag,
                "uses": int(s["count"]),
                "avg_views": int(s["views"] / s["count"]) if s["count"] else 0,
                "avg_engagement": round(s["engagement_sum"] / s["count"], 4)
                if s["count"]
                else 0,
            }
            for tag, s in tag_stats.items()
        ),
        key=lambda x: (x["uses"], x["avg_views"]),
        reverse=True,
    )

    weekday_counts = Counter(v["weekday"] for v in videos if v["weekday"])
    hour_counts = Counter(v["hour_utc"] for v in videos if v["hour_utc"] is not None)

    # Hook = erste 40 Zeichen der Caption (Proxy für den On-Screen-/Text-Hook)
    hooks = [
        {
            "hook": (v["description"][:40] + "…") if len(v["description"]) > 40 else v["description"],
            "views": v["views"],
            "engagement_rate": v["engagement_rate"],
            "url": v["url"],
        }
        for v in videos
    ]

    by_views = sorted(videos, key=lambda v: v["views"], reverse=True)
    by_engagement = sorted(videos, key=lambda v: v["engagement_rate"], reverse=True)

    return {
        "video_count": len(videos),
        "uploader": videos[0]["uploader"],
        "totals": totals,
        "averages": {
            "views": int(mean(views_series)),
            "views_median": int(median(views_series)),
            "engagement_rate": round(mean(v["engagement_rate"] for v in videos), 4),
            "duration_s": round(mean(v["duration_s"] or 0 for v in videos), 1),
        },
        "top_by_views": [
            {"url": v["url"], "views": v["views"], "likes": v["likes"], "caption": v["description"][:120]}
            for v in by_views[:10]
        ],
        "top_by_engagement": [
            {
                "url": v["url"],
                "views": v["views"],
                "engagement_rate": v["engagement_rate"],
                "caption": v["description"][:120],
            }
            for v in by_engagement[:10]
            if v["views"] >= 500  # Rauschen kleiner-View-Ausreisser filtern
        ][:10],
        "hashtags_ranked": hashtags_ranked[:30],
        "weekday_post_counts": dict(weekday_counts.most_common()),
        "hour_utc_post_counts": dict(sorted(hour_counts.items())),
        "hooks": hooks,
    }


def render_markdown(report: dict[str, Any]) -> str:
    if not report.get("video_count"):
        return "# TikTok Analyse\n\nKeine Videos gefunden.\n"

    lines: list[str] = []
    lines.append(f"# TikTok-Analyse — @{report['uploader']}")
    lines.append("")
    lines.append(f"_Generiert: {datetime.now(tz=timezone.utc).isoformat()}_")
    lines.append("")
    lines.append("## Übersicht")
    lines.append("")
    t = report["totals"]
    a = report["averages"]
    lines.append(f"- Videos analysiert: **{report['video_count']}**")
    lines.append(f"- Gesamt-Views: **{t['views']:,}**")
    lines.append(f"- Gesamt-Likes: **{t['likes']:,}**")
    lines.append(f"- Gesamt-Comments: **{t['comments']:,}**")
    lines.append(f"- Gesamt-Shares: **{t['shares']:,}**")
    lines.append(f"- Ø Views / Video: **{a['views']:,}** (Median {a['views_median']:,})")
    lines.append(f"- Ø Engagement-Rate: **{a['engagement_rate'] * 100:.2f}%**")
    lines.append(f"- Ø Videolänge: **{a['duration_s']:.1f}s**")
    lines.append("")

    lines.append("## Top 10 nach Views")
    lines.append("")
    lines.append("| Views | Likes | Caption | URL |")
    lines.append("|---:|---:|---|---|")
    for v in report["top_by_views"]:
        cap = v["caption"].replace("|", "/").replace("\n", " ")
        lines.append(f"| {v['views']:,} | {v['likes']:,} | {cap} | {v['url']} |")
    lines.append("")

    lines.append("## Top 10 nach Engagement-Rate (≥500 Views)")
    lines.append("")
    lines.append("| Eng. % | Views | Caption | URL |")
    lines.append("|---:|---:|---|---|")
    for v in report["top_by_engagement"]:
        cap = v["caption"].replace("|", "/").replace("\n", " ")
        lines.append(
            f"| {v['engagement_rate'] * 100:.2f}% | {v['views']:,} | {cap} | {v['url']} |"
        )
    lines.append("")

    lines.append("## Hashtag-Performance (Top 30)")
    lines.append("")
    lines.append("| Tag | Verwendet | Ø Views | Ø Engagement |")
    lines.append("|---|---:|---:|---:|")
    for h in report["hashtags_ranked"]:
        lines.append(
            f"| #{h['tag']} | {h['uses']} | {h['avg_views']:,} | {h['avg_engagement'] * 100:.2f}% |"
        )
    lines.append("")

    lines.append("## Posting-Pattern")
    lines.append("")
    lines.append("**Wochentage:**  " + ", ".join(
        f"{day}: {n}" for day, n in report["weekday_post_counts"].items()
    ))
    lines.append("")
    lines.append("**Stunde (UTC):**  " + ", ".join(
        f"{h:02d}h: {n}" for h, n in report["hour_utc_post_counts"].items()
    ))
    lines.append("")

    lines.append("## Hooks (Caption-Anfang) je Video")
    lines.append("")
    lines.append("| Views | Eng. % | Hook |")
    lines.append("|---:|---:|---|")
    for h in sorted(report["hooks"], key=lambda x: x["views"], reverse=True):
        hook = h["hook"].replace("|", "/").replace("\n", " ")
        lines.append(f"| {h['views']:,} | {h['engagement_rate'] * 100:.2f}% | {hook} |")
    lines.append("")

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="LuxeStyle: TikTok-Profil/Video-Liste analysieren.")
    g = p.add_mutually_exclusive_group(required=False)
    g.add_argument("--user", help=f"TikTok-Username (mit/ohne @) oder Profil-URL (Default {DEFAULT_USER})")
    g.add_argument("--urls", type=Path, help="Textdatei mit einer Video-URL pro Zeile")
    p.add_argument(
        "--seed-video",
        help="Eine Video-URL des Ziel-Users, um die interne channel_id zu finden, "
        "falls die direkte --user-Extraktion scheitert.",
    )
    p.add_argument(
        "--channel-id",
        help="Interne TikTok channel_id (secUid). Umgeht den fehlerhaften User-Extractor.",
    )
    p.add_argument("--max", type=int, default=30, help="Max. Videos (Default 30)")
    p.add_argument(
        "--insecure",
        action="store_true",
        help="--no-check-certificate an yt-dlp durchreichen. Nur in Sandbox-/"
        "MITM-Proxy-Umgebungen nötig.",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("reports"),
        help="Ausgabeordner (Default ./reports)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    check_yt_dlp()

    global INSECURE
    INSECURE = args.insecure

    # Default-User, wenn weder --user noch --urls angegeben
    if not args.user and not args.urls:
        args.user = DEFAULT_USER

    if args.user:
        label = args.user.lstrip("@").rstrip("/").split("/")[-1]
        channel_id = args.channel_id
        if not channel_id and args.seed_video:
            channel_id = discover_channel_id(args.seed_video)

        if channel_id:
            target = f"tiktokuser:{channel_id}"
            raw, _ = fetch_metadata(target, args.max, raise_on_error=True)
        else:
            target = normalize_user(args.user)
            raw, err = fetch_metadata(target, args.max)
            if not raw and SECONDARY_ID_ERR in err:
                die(
                    "yt-dlp kann diesen User nicht direkt auflösen (TikTok-Backend-Eigenheit).\n"
                    "Workaround: eine beliebige Video-URL des Profils kopieren und "
                    "mit --seed-video <url> erneut starten, z.B.:\n"
                    f"  python3 tiktok_analyze.py --user {args.user} "
                    "--seed-video https://www.tiktok.com/@.../video/..."
                )
            if not raw:
                die(f"yt-dlp lieferte keine Videos. Stderr:\n{err.strip()}")
    else:
        if not args.urls.exists():
            die(f"--urls Datei nicht gefunden: {args.urls}")
        urls = [
            ln.strip()
            for ln in args.urls.read_text().splitlines()
            if ln.strip() and not ln.strip().startswith("#")
        ]
        if not urls:
            die("--urls Datei ist leer")
        raw = []
        for url in urls:
            vids, _ = fetch_metadata(url, None, raise_on_error=True)
            raw.extend(vids)
        label = args.urls.stem

    videos = [slim(v) for v in raw if v]
    print(f"→ {len(videos)} Video(s) geparst", file=sys.stderr)

    report = analyze(videos)

    args.out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    json_path = args.out / f"tiktok_{label}_{stamp}.json"
    md_path = args.out / f"tiktok_{label}_{stamp}.md"

    json_path.write_text(
        json.dumps({"videos": videos, "report": report}, indent=2, ensure_ascii=False)
    )
    md_path.write_text(render_markdown(report))

    print(f"✓ geschrieben {json_path}", file=sys.stderr)
    print(f"✓ geschrieben {md_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
