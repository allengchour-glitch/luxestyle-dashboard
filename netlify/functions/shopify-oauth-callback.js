// netlify/functions/shopify-oauth-callback.js
// Empfaengt OAuth-Code von Shopify (Redirect-URL = /) und tauscht ihn
// gegen einen shpat_-Token. Speichert Token in Netlify Blobs.
// Wenn keine OAuth-Parameter da sind, normales Dashboard ausliefern.

import { getStore } from '@netlify/blobs';

export default async (request, context) => {
      const url = new URL(request.url);
      const code = url.searchParams.get('code');
      const shop = url.searchParams.get('shop');

      // Keine OAuth-Parameter -> normale Auslieferung der index.html
      // (next() laesst das statische Asset durch)
      if (!code || !shop) {
              return context.next();
      }

      // Shop-Domain validieren
      if (!/^[a-zA-Z0-9][a-zA-Z0-9-]*\.myshopify\.com$/.test(shop)) {
              return new Response('Ungueltige Shop-Domain', { status: 400 });
      }

      const clientId = process.env.SHOPIFY_CLIENT_ID;
      const clientSecret = process.env.SHOPIFY_API_SECRET;

      if (!clientId || !clientSecret) {
              return new Response('Server nicht konfiguriert (SHOPIFY_CLIENT_ID/SHOPIFY_API_SECRET fehlen in Netlify Env Vars)', { status: 500 });
      }

      // Token-Tausch bei Shopify
      const tokenResp = await fetch(`https://${shop}/admin/oauth/access_token`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                        client_id: clientId,
                        client_secret: clientSecret,
                        code: code
              })
      });

      if (!tokenResp.ok) {
              const errText = await tokenResp.text();
              return new Response(`Token-Tausch fehlgeschlagen (${tokenResp.status}): ${errText}`, { status: 502 });
      }

      const tokenData = await tokenResp.json();
      const accessToken = tokenData.access_token;

      if (!accessToken || !accessToken.startsWith('shpat_')) {
              return new Response('Kein gueltiger shpat_-Token erhalten', { status: 502 });
      }

      // Token in Netlify Blobs speichern
      const store = getStore('shopify-tokens');
      await store.setJSON(shop, {
              access_token: accessToken,
              scope: tokenData.scope,
              shop: shop,
              installed_at: new Date().toISOString()
      });

      // Weiter zum Dashboard mit Erfolgs-Flag (ohne sensible Parameter)
      return new Response(null, {
              status: 302,
              headers: {
                        Location: `/?shopify_connected=1&shop=${encodeURIComponent(shop)}`
              }
      });
};

export const config = {
      path: '/'
};
