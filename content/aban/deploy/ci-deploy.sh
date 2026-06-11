#!/usr/bin/env bash
# Deployt den aban-news Worker automatisch (fuer GitHub Actions / aban-worker-deploy.yml).
# Erwartet ENV: CLOUDFLARE_API_TOKEN (+ optional CLOUDFLARE_ACCOUNT_ID),
#               UNSUB_SECRET, RESEND_API_KEY, MAIL_FROM, ADMIN_KEY.
# Macht: KV anlegen/finden -> ID in wrangler.toml einsetzen -> Secrets setzen -> deploy
# (custom_domain provisioniert DNS + Zertifikat fuer api.abannews.com automatisch).
set -euo pipefail
cd "$(dirname "$0")"

WR="npx --yes wrangler"

echo "== 1) KV-Namespace ABAN_SUBS sicherstellen =="
create_out="$($WR kv namespace create ABAN_SUBS 2>&1 || true)"
kv_id="$(printf '%s' "$create_out" | grep -oE '[a-f0-9]{32}' | head -1 || true)"
if [ -z "$kv_id" ]; then
  echo "   (existiert evtl. schon) -> in Liste suchen"
  kv_id="$($WR kv namespace list | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{try{const a=JSON.parse(s);const m=a.find(x=>String(x.title).endsWith("ABAN_SUBS"));process.stdout.write(m?m.id:"")}catch(e){}})')"
fi
[ -n "$kv_id" ] || { echo "FEHLER: KV-ID nicht ermittelbar"; exit 1; }
echo "   KV-ID: $kv_id"
sed -i.bak "s/REPLACE_WITH_KV_ID/$kv_id/" wrangler.toml && rm -f wrangler.toml.bak

echo "== 2) Secrets setzen (Werte aus ENV, nie geloggt) =="
for s in UNSUB_SECRET RESEND_API_KEY MAIL_FROM ADMIN_KEY; do
  val="${!s:-}"
  if [ -n "$val" ]; then
    printf '%s' "$val" | $WR secret put "$s" >/dev/null && echo "   gesetzt: $s"
  else
    echo "   WARN: $s ist leer (uebersprungen)"
  fi
done

echo "== 3) Worker deployen (inkl. Custom Domain api.abannews.com) =="
$WR deploy

echo "== Fertig. Test: https://api.abannews.com/subscribe =="
