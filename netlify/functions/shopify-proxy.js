// netlify/functions/shopify-proxy.js
// Sicherer Proxy zwischen Dashboard und Shopify Admin API.
// Liest shpat_-Token aus Netlify Blobs, erlaubt nur whitelisted Endpoints.

import { getStore } from '@netlify/blobs';

const API_VERSION = '2024-10';

const ALLOWED = [
    /^shop\.json$/,
    /^products\.json(\?.*)?$/,
    /^products\/count\.json(\?.*)?$/,
    /^products\/\d+\.json$/,
    /^products\/\d+\/images\.json$/,
    /^products\/\d+\/variants\.json$/,
    /^variants\/\d+\.json$/,
    /^orders\.json(\?.*)?$/,
    /^orders\/count\.json(\?.*)?$/,
    /^orders\/\d+\.json$/,
    /^orders\/\d+\/fulfillments\.json$/,
    /^customers\.json(\?.*)?$/,
    /^customers\/count\.json(\?.*)?$/,
    /^customers\/\d+\.json$/,
    /^themes\.json$/,
    /^themes\/\d+\.json$/,
    /^themes\/\d+\/assets\.json(\?.*)?$/,
    /^price_rules\.json(\?.*)?$/,
    /^price_rules\/\d+\.json$/,
    /^discount_codes\/lookup\.json(\?.*)?$/,
    /^inventory_items\.json(\?.*)?$/,
    /^inventory_levels\.json(\?.*)?$/,
    /^locations\.json$/,
    /^smart_collections\.json(\?.*)?$/,
    /^custom_collections\.json(\?.*)?$/,
    /^collects\.json(\?.*)?$/,
    /^pages\.json(\?.*)?$/,
    /^blogs\.json(\?.*)?$/,
    /^webhooks\.json(\?.*)?$/
  ];

function isAllowed(endpoint) {
    return ALLOWED.some(rx => rx.test(endpoint));
}

export default async (request) => {
    const url = new URL(request.url);
    const endpoint = url.pathname.replace(/^\/api\/shopify\//, '') + url.search;

    if (!isAllowed(endpoint)) {
          return new Response(JSON.stringify({ error: 'Endpoint nicht erlaubt', endpoint }),
                              { status: 403, headers: { 'Content-Type': 'application/json' } });
    }

    const shop = process.env.SHOPIFY_SHOP;
    if (!shop) {
          return new Response(JSON.stringify({ error: 'SHOPIFY_SHOP fehlt' }),
                              { status: 500, headers: { 'Content-Type': 'application/json' } });
    }

    const store = getStore('shopify-tokens');
    const tokenData = await store.get(shop, { type: 'json' });

    if (!tokenData || !tokenData.access_token) {
          return new Response(JSON.stringify({
                  error: 'Kein Token gespeichert',
                  install_url: '/auth/shopify/install'
          }), { status: 401, headers: { 'Content-Type': 'application/json' } });
    }

    const shopifyUrl = `https://${shop}/admin/api/${API_VERSION}/${endpoint}`;
    const headers = {
          'X-Shopify-Access-Token': tokenData.access_token,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
    };

    let body;
    if (request.method !== 'GET' && request.method !== 'HEAD') {
          body = await request.text();
    }

    const shopifyResp = await fetch(shopifyUrl, { method: request.method, headers, body });
    const respText = await shopifyResp.text();

    return new Response(respText, {
          status: shopifyResp.status,
          headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }
    });
};

export const config = { path: '/api/shopify/*' };
