// netlify/functions/shopify-oauth-callback.js
// Empfaengt den OAuth-Code von Shopify nach App-Installation,
// tauscht ihn gegen einen permanenten shpat_-Token und speichert
// diesen verschluesselt in Netlify Blobs.

import { getStore } from '@netlify/blobs';

export default async (request, context) => {
    const url = new URL(request.url);
    const code = url.searchParams.get('code');
    const shop = url.searchParams.get('shop');
    const hmac = url.searchParams.get('hmac');
    const state = url.searchParams.get('state');

    // Grundvalidierung
    if (!code || !shop) {
          return new Response('Fehlende Parameter (code/shop)', { status: 400 });
    }

    // Shop-Domain muss .myshopify.com sein
    if (!/^[a-zA-Z0-9][a-zA-Z0-9-]*\.myshopify\.com$/.test(shop)) {
          return new Response('Ungueltige Shop-Domain', { status: 400 });
    }

    const clientId = process.env.SHOPIFY_CLIENT_ID;
    const clientSecret = process.env.SHOPIFY_API_SECRET;

    if (!clientId || !clientSecret) {
          return new Response('Server nicht konfiguriert (Env Vars fehlen)', { status: 500 });
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
          return new Response(`Token-Tausch fehlgeschlagen: ${errText}`, { status: 502 });
    }

    const tokenData = await tokenResp.json();
    const accessToken = tokenData.access_token;
    const scope = tokenData.scope;

    if (!accessToken || !accessToken.startsWith('shpat_')) {
          return new Response('Kein gueltiger shpat_-Token erhalten', { status: 502 });
    }

    // Token in Netlify Blobs speichern (verschluesselt, nur Functions koennen lesen)
    const store = getStore('shopify-tokens');
    await store.setJSON(shop, {
          access_token: accessToken,
          scope: scope,
          shop: shop,
          installed_at: new Date().toISOString()
    });

    // Erfolgreich -> zurueck zum Dashboard mit Erfolgs-Flag
    return new Response(null, {
          status: 302,
          headers: {
                  Location: `/?shopify_connected=1&shop=${encodeURIComponent(shop)}`
          }
    });
};

export const config = {
    path: '/auth/shopify/callback'
};
