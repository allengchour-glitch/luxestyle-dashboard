# Worker-Deploy in 6 Kommandos (Wrangler-CLI)

Statt Copy-Paste im Cloudflare-Dashboard: der Worker geht per CLI live. Das Einzige, was du
beisteuern musst, ist **ein Login** (`wrangler login` öffnet den Browser zu deinem Cloudflare-Konto)
und die **Secret-Werte**. Den Rest erledigen die Kommandos.

```bash
cd content/aban/deploy

# 1. Wrangler installieren
npm install

# 2. Bei deinem Cloudflare-Konto anmelden (oeffnet Browser)
npx wrangler login

# 3. KV-Namespace anlegen -> gibt eine id aus
npx wrangler kv namespace create ABAN_SUBS
#    -> die ausgegebene id in wrangler.toml bei REPLACE_WITH_KV_ID eintragen

# 4. Secrets setzen (Werte werden interaktiv abgefragt, nie im Klartext im Repo)
npx wrangler secret put UNSUB_SECRET     # dein generiertes Geheimnis (ueberall gleich!)
npx wrangler secret put RESEND_API_KEY   # aus dem Resend-Konto
npx wrangler secret put MAIL_FROM        # z.B.  aban news <news@abannews.com>
npx wrangler secret put ADMIN_KEY        # zweites Geheimnis fuer /export

# 5. Deployen
npx wrangler deploy

# 6. Testen (Browser): https://<dein-worker>.workers.dev/subscribe  -> "aban news subscribe service"
```

## Routen auf abannews.com
`wrangler.toml` enthält schon die Routen `abannews.com/subscribe|confirm|status|abmelden|export`.
Sie greifen, sobald `abannews.com` als Zone in deinem Cloudflare-Konto liegt. Willst du zuerst nur
über `*.workers.dev` testen, kommentiere den `routes`-Block vor dem ersten Deploy aus.

## Landing als Cloudflare Pages
```bash
cd content/aban
npx wrangler pages deploy landing --project-name aban-news
```
Danach `abannews.com` (oder `www`) im Pages-Projekt als Custom Domain zuweisen.

## Wichtig
- `UNSUB_SECRET` muss **identisch** sein mit dem GitHub-Secret (sonst stimmen die Confirm-/Abmelde-Links nicht).
- Vor Mailversand SPF/DKIM für `abannews.com` bei Resend verifizieren (sonst Spam).
- Volle Erklaerung aller Schritte: `../DEPLOY_ANLEITUNG.md`.
