// netlify/functions/shopify-oauth-callback.js
// Faengt alle Requests auf / ab.
// - Bei OAuth-Callback (code+shop+hmac): Tausch gegen Token, Speicherung in Blobs.
// - Bei normalen Besuchen ohne OAuth-Parameter: Liefert die statische index.html aus.
import { getStore } from '@netlify/blobs';

export default async (request, context) => {
        const url = new URL(request.url);
        const code = url.searchParams.get('code');
        const shop = url.searchParams.get('shop');
        const hmac = url.searchParams.get('hmac');

        // Keine OAuth-Parameter -> normales Dashboard ausliefern
        if (!code || !shop || !hmac) {
                  try {
                              const indexResp = await fetch(`${url.origin}/index.html`);
                              if (indexResp.ok) {
                                            const html = await indexResp.text();
                                            return new Response(html, {
                                                            status: 200,
                                                            headers: { 'content-type': 'text/html; charset=utf-8' }
                                            });
                              }
                  } catch (e) {
                              console.error('Fehler beim Laden der index.html:', e);
                  }
                  return new Response('Dashboard nicht erreichbar.', { status: 500 });
        }

        // Shop-Domain validieren
        if (!/^[a-zA-Z0-9][a-zA-Z0-9-]*\.myshopify\.com$/.test(shop)) {
                  return new Response('Ungueltige Shop-Domain', { status: 400 });
        }

        const clientId = process.env.SHOPIFY_CLIENT_ID;
        const clientSecret = process.env.SHOPIFY_API_SECRET;

        if (!clientId || !clientSecret) {
                  return new Response('Server-Konfiguration unvollstaendig.', { status: 500 });
        }

        try {
                  const tokenResp = await fetch(`https://${shop}/admin/oauth/access_token`, {
                              method: 'POST',
                              headers: { 'content-type': 'application/json' },
                              body: JSON.stringify({
                                            client_id: clientId,
                                            client_secret: clientSecret,
                                            code: code
                              })
                  });

          if (!tokenResp.ok) {
                      const errTxt = await tokenResp.text();
                      console.error('Shopify Token-Tausch fehlgeschlagen:', errTxt);
                      return new Response('Token-Tausch fehlgeschlagen.', { status: 502 });
          }

          const tokenJson = await tokenResp.json();
                  const accessToken = tokenJson.access_token;

          if (!accessToken) {
                      return new Response('Kein Access Token erhalten.', { status: 502 });
          }

          const store = getStore('shopify-tokens');
                  await store.set(shop, JSON.stringify({
                              access_token: accessToken,
                              scope: tokenJson.scope || '',
                              installed_at: new Date().toISOString()
                  }));

          return Response.redirect(`${url.origin}/?installed=1&shop=${encodeURIComponent(shop)}`, 302);
        } catch (e) {
                  console.error('Fehler im OAuth-Callback:', e);
                  return new Response('Interner Fehler beim OAuth-Callback.', { status: 500 });
        }
};

export const config = {
        path: '/'
};
