// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import vercel from '@astrojs/vercel';

export default defineConfig({
  site: 'https://www.markgores.com',
  // Pages stay prerendered (static); the adapter exists only so
  // src/pages/api/* endpoints with prerender=false run as functions.
  adapter: vercel(),
  redirects: {
    // Listing plan temporarily hidden (July 2026): an active listing is at
    // 3%, the page publishes 2.7%. Page lives in src/hidden/how-i-sell.astro;
    // move it back to src/pages/ and remove this redirect to restore.
    '/how-i-sell': { status: 302, destination: '/' },
  },
  integrations: [
    sitemap({
      // Allowlist: private client proposal pages must never appear in the
      // public sitemap. Add new PUBLIC pages here explicitly.
      filter: (page) =>
        page === 'https://www.markgores.com/' ||
        page === 'https://www.markgores.com/vendors/' ||
        page === 'https://www.markgores.com/listings/8204-horizon-drive/' ||
        page === 'https://www.markgores.com/listings/16288-florida-way/'
    })
  ],
  build: {
    inlineStylesheets: 'auto'
  }
});
