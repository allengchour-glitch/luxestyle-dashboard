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
# Robust: ERST bestehenden Namespace finden (echte ID), nur anlegen wenn keiner existiert.
find_kv() { $WR kv namespace list 2>/dev/null | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{try{const a=JSON.parse(s);const m=a.find(x=>String(x.title).endsWith("ABAN_SUBS"));process.stdout.write(m?m.id:"")}catch(e){}})'; }
kv_id="$(find_kv)"
if [ -z "$kv_id" ]; then
  echo "   keiner vorhanden -> anlegen"
  $WR kv namespace create ABAN_SUBS >/dev/null 2>&1 || true
  kv_id="$(find_kv)"
fi
echo "$kv_id" | grep -qE '^[a-f0-9]{32}$' || { echo "FEHLER: KV-ID ungueltig/leer: '$kv_id'"; exit 1; }
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
