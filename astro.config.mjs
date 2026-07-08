// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://markgores.com',
  integrations: [
    sitemap({
      // Allowlist: private client proposal pages must never appear in the
      // public sitemap. Add new PUBLIC pages here explicitly.
      filter: (page) =>
        page === 'https://markgores.com/' ||
        page === 'https://markgores.com/how-i-sell/'
    })
  ],
  build: {
    inlineStylesheets: 'auto'
  }
});
