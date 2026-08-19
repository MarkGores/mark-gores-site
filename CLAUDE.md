# Mark Gores Site (markgores.com)

## What this is
Astro 5 site for Mark Gores, RE/MAX Advantage Plus realtor in Prior Lake, Minnesota. Public homepage at `/`, plus private listing proposal pages (noindex) for active sellers. Auto-deploys to Vercel from `main` in ~90s.

## Tech Stack
- **Framework:** Astro 5 (static), TypeScript
- **Styling:** Plain CSS with CSS variables in `src/styles/global.css`. No framework.
- **Hosting:** Vercel, auto-deploys from `main`
- **Repo:** github.com/MarkGores/mark-gores-site

## Brand & Design System

### Colors (CSS variables)
- `--cream` `#F5F0E8` page background
- `--dark` `#1A1A18` primary text and dark sections
- `--warm` `#8B7355` mono labels, soft accents
- `--accent` `#4A7BC8` (blue) emphasis, highlights, prices
- `--sage` `#7A8B6F` secondary accent
- `--light-warm` `#E8DFD0` borders, soft backgrounds

### Typography
- `--serif` 'DM Serif Display' display headlines, big numbers
- `--body` 'Newsreader' body copy
- `--mono` 'JetBrains Mono' labels, table cells, monetary values

### Aesthetic
Editorial / magazine, deliberately not "generic realtor". Lots of whitespace. Section labels in mono uppercase with a leading dash. Dark sections sparingly for emphasis.

## Brand Voice

Mark's voice is the most important thing on this site. Generic AI/marketing phrasing is immediately obvious to him.

### Hard rules (do not violate)
- **NO em-dashes or en-dashes ANYWHERE.** Use commas, periods, parentheses, colons. Every output gets grep'd for these.
- **NO overpromises.** Never "almost certainly sell fast", "expect strong offers in week one", "guaranteed". Mark sells trust by not overselling.
- **NO hokey marketing language.** "No pitch. No pressure. Just the work." / "you'd be the only one on this shelf" / "your home is in its own lane" are all out.
- **NO "happens to" phrasing** (implies surprise). Just state the quality directly.
- **NO condescending lines** like "this stuff matters more than most sellers realize."
- **NO dramatic data framing** like "the data is pretty clear, and it matters for you." State facts. Let data speak.
- **NO defensive lines** like "these are real numbers, not estimates."

### Soft rules
- **Specific details over generic claims.** "$559,999 at 109 days on market" beats "a stale listing."
- **Round numbers for pricing.** Charm pricing ($564,900) doesn't help. Round numbers signal confidence.
- **Use Mark's exact phrasings when given.** Don't paraphrase.
- **Conversational, direct, short sentences.** Read `src/pages/index.astro` for tone.
- **Heavy contractions.** I'll, that's, here's, you're, we've, it's.
- **Sentence fragments are fine.** They feel like talking.
- **When you don't know something specific, ask Mark.** Don't invent property details.

## Listing Proposal Pages

### What they are
Private (noindex) one-off pages built per listing presentation. Custom CMA + marketing proposal + fee breakdown + net sheet for a specific seller. Lives at `markgores.com/{slug}`.

**Two templates, copy one end to end (don't hand-build):**
- `src/pages/8595-moraine-drive.astro` (April 2026, Shakopee): standard owner-occupant sale. Hero photo, "For [Names]", full marketing-card grid, static net-sheet block.
- `src/pages/6051-160th-street.astro` (July 2026, estate): data-first / estate / investor / unusual listings. Facts-card hero, comps table, a dark "reasoning" section (e.g. why it prices as a single-family, not a duplex), an optional condition photo gallery, and an **interactive cost estimator** that mirrors Trademark's net-sheet math. Its photos went through a HEIC EXIF-orientation fix (bake with Python PIL `exif_transpose`, not `sips` rotation); reuse that pipeline. This one drew explicit praise from the prospect.

Read the chosen template end-to-end before building. Copy its structure exactly.

### Privacy
Use `noindex={true}` prop on `BaseLayout` for every proposal page.

### Required sections (in order)
1. **Custom nav** with homeowner names + month/year
2. **Hero** with "For [Names]" h1, address subtitle, conversational opener, photo, "Mark" signature
3. **Recommendation** with big accent-colored list price, three tiers (Safe / Recommended / Stretch), rationale, charm-pricing callout
4. **Specs** with 8-cell grid + narrative paragraph about updates
5. **Comps table** with six matched sold comps + dark "Adjusted to your home" callout + optional OneHome portal link
6. **Street proof (dark section)** with neighborhood solds card grid + active card in accent
7. **Active listings** with prices + DOM chips + new construction context
8. **Marketing plan** with 6 cards (Pre-Listing, Photography & Media, Advertising & Exposure, Communication, Offers & Negotiation, Local Expertise)
9. **Fees** with 2.7% headline, fee row breakdown
10. **Net proceeds**: the interactive cost estimator (preferred, see 6051) or a static dark card, itemized on Trademark's fees
11. **Closing** respecting their decision-making process, no pressure
12. **Footer** with disclaimer and brokerage attribution

### Data sources
- **Subject + comps:** local SQLite at `/Users/markmini/Projects/prior-lake-ecosystem/PriorLake.RealEstate/data/listings.db` (~870K NorthstarMLS listings, updated every 15 min)
  - `ListingId` has `NST` prefix. User MLS#s may differ; search broadly.
  - No `LotSizeAcres` or `UnparsedAddress` column. Use `LotSizeArea`/`LotSizeUnits`. Build address from `StreetNumber || StreetName || StreetSuffix`.
  - Key columns: `StreetNumber`, `StreetName`, `SubdivisionName`, `ListPrice`, `ClosePrice`, `CloseDate`, `DaysOnMarket`, `BedroomsTotal`, `BathroomsTotalInteger`, `LivingArea`, `AboveGradeFinishedArea`, `BelowGradeFinishedArea`, `FoundationArea`, `YearBuilt`, `LotSizeArea`, `GarageSpaces`, `Basement`, `ArchitecturalStyle`
  - **`PropertySubType` has TWO conventions in the data: `'Single Family Residence'` (older listings, ~4,000 in 55379) and `'Single Family'` (newer listings including most new construction, ~400 in 55379). When filtering, always use `PropertySubType IN ('Single Family Residence','Single Family')` or you will silently miss the new builds.**
- **Net sheet:** self-serve via Trademark Title's TitleCapture tool (Mark enters inputs, fees auto-populate); Marti does not run it by hand. The site's cost estimator already encodes Trademark's seven-county-metro fees: settlement $595, conservation $5, transaction $625, MN state deed tax 0.33%, plus the listing and buyer brokerage %s.
- **Property details, names, context:** Ask Mark.

### Workflow for a new proposal
1. Get address/MLS# and any starting context from Mark.
2. Query local SQLite DB for the subject property.
3. Pull 8-12 candidate comps (similar sqft, age, basement, garage, area). Show Mark, let him pick 6.
4. Pull street/subdivision recent solds and current actives in relevant price band.
5. **Pull Mark's own record near the subject** (never skip this; a 2026 listing was lost partly because his neighborhood sales went unmentioned). Query `ListAgentMlsId`, `CoListAgentMlsId`, or `BuyerAgentMlsId` = `NST505006408` (co-list partners: `NST502001768`, `NST505002586`) filtered to the subject's city/subdivision. If anything relevant exists, include a "My record near you" section in the proposal. His MLS-ID counts understate his career (sales ran through his mom's number for years), so ask Mark about pre-2012 or partner-side sales near the subject too.
6. Ask Mark for: homeowner names, recommended price, updates narrative, target close timeframe, any personal context about sellers.
7. Net proceeds: use the interactive cost estimator (Trademark's fees are already encoded, see 6051). For an exact figure, Mark runs the property on Trademark's self-serve TitleCapture tool.
8. Build page in `src/pages/{slug}.astro` copying the structure of the chosen template (8595 standard, or 6051 data-first/estate).
9. Save hero photo to `public/images/{slug}-front.jpg`.
10. Verify page renders. Sweep for em-dashes (grep must return zero).
11. Show Mark screenshots of every section, get explicit signoff.
12. Commit only the proposal files (not unrelated working-tree changes). Push to deploy.

### Slug convention
Street-address kebab-case: `8595-moraine-drive`, `1234-main-street`, `709-lakefront-court`.

### Common landmines
- Don't sweep up unrelated working-tree changes when committing.
- Don't include sensitive backstory (insurance claims, water damage, divorce, finances) in the proposal. That's disclosure-stage information.
- Don't paraphrase Mark's specific phrases. Use them verbatim.
- Don't add em-dashes. This bears repeating.

## /vendors (Service Providers page)
Public page mirroring the Minnesota Real Estate Team's vendor list (MNRET approved this in writing, July 2026; attribution on the page is part of the deal). Situation-grouped accordions + keyword search + an LLM "who to call" helper.

- **Data:** `src/data/vendors.json` is scraped, never hand-edit. `scripts/scrape_vendors.py` (stdlib Python) scrapes mnrealestateteamvendors.com, excludes realtor-only/lifestyle categories, normalizes dashes, refuses to write if the page shape changes. `.github/workflows/refresh-vendors.yml` reruns it monthly and commits only on change.
- **Taxonomy:** `src/data/vendor-groups.json` is hand-curated: 10 situation groups, display-merged near-duplicate categories, per-section search keywords. New MNRET categories not mapped there fall into a "More" group on the page automatically.
- **LLM helper:** `src/pages/vendor-route.ts (served at /vendor-route; root api/ is Vercel-reserved for the contact function and 404s other /api paths)` (serverless via `@astrojs/vercel@8`, pinned for Astro 5). Opus 4.8, structured output constrained to an enum of section slugs, server-side allowlist, catalog filtered to sections that actually render, prompt caching, per-IP + global rate limit, Origin required. Needs `ANTHROPIC_API_KEY` in Vercel env; without it the endpoint 503s and the page falls back to keyword search. Keep a monthly spend limit on the Anthropic workspace as the hard cost backstop.
- Frontend falls back to keyword search (word-AND, then any-word) whenever the endpoint fails; never show a hard error to a visitor.

## Deploy
Push to `main`. Vercel auto-builds in ~90s. Apex 307-redirects to `www.markgores.com`.

### Sitemap & indexing
- **Canonical host is `https://www.markgores.com`** (since Aug 19 2026): `site` in astro.config, `siteUrl` in BaseLayout, robots.txt, JSON-LD and the sitemap allowlist all use www, matching Vercel's apex->www 307. Never reintroduce apex URLs.
- The sitemap is an **allowlist** in `astro.config.mjs` (public pages: `/`, `/vendors/`, `/savage/`, `/prior-lake-realtor/`, plus the two public listing pages). Private proposal pages must never be added. When creating a new PUBLIC page, add its URL to the filter or it won't be in the sitemap.
- **Public doc pages (Aug 2026):** `/savage` (office address 13875 Hwy 13 S, dated market snapshot from the MLS replica, 719/191 school split) and `/prior-lake-realtor` (how to pick an agent + the facts about Mark). Both drafted by Claude from verifiable facts only, following the voice rules, WITHOUT Mark's line-by-line review; he should read them. Snapshot numbers in savage.astro are hand-entered constants (refresh when touched).
- `/how-i-sell` is TEMPORARILY HIDDEN (July 13, 2026): an active listing is at 3% while the page published 2.7%. The page is parked at `src/hidden/how-i-sell.astro` with 302/307 redirects to `/` (astro.config redirects + vercel.json), out of the sitemap, and the homepage sell section was rewritten fee-free. Do not restore or re-add fee mentions until Mark says the 3% listing is resolved. Restore: git mv back to src/pages/, remove both redirects, re-add sitemap entry, restore the index.astro sell section (pre-hide copy at commit ee4c126). Proposal pages stay `noindex={true}` AND out of the sitemap; both protections are needed (noindex alone still leaked addresses via the sitemap until July 2026).

### Useful commands
```bash
# Build locally
PATH="/opt/homebrew/bin:$PATH" node node_modules/.bin/astro build

# Dev server (port 4321)
PATH="/opt/homebrew/bin:$PATH" node node_modules/.bin/astro dev

# Em-dash sweep (must return empty; covers layouts too, a dash hid in BaseLayout's meta description once)
grep -rn '—\|–' src/
```

## Vendors & Contacts
- **Trademark Title** Marti Mahoney-Peterson, Executive Closer. martim@trademarktitle.com, 952-226-7905. She's the closer; net sheets are self-serve via Trademark's TitleCapture site (Mark fills inputs, fees populate), not run by hand.
- **Brokerage** RE/MAX Advantage Plus
- **Mark** 612-201-5447, mark@markgores.com

## Fee Structure (2026)
- **Listing fee:** 2.7% standard, but NOT currently published anywhere public (see /how-i-sell hidden note above; one active listing is at 3%). Earlier proposals (Moraine, Horizon) quoted 2.5%; do not reuse that number.
- **Buyer side:** plan on 2.7% local norm post-NAR settlement, sometimes negotiable to 2.5%
- **Total seller outlay:** ~5.4% plus MN deed tax (0.33%) and ~$1,225 Trademark title/closing fees (settlement $595 + conservation $5 + transaction $625)
- Included in 2.7%: staging consult, professional + aerial photography, written MLS photo captions, print/radio/online/social advertising, weekly written analytics updates, direct phone access, offer review, contract-to-close management, private per-seller proposal page.

## Cross-Repo Reference
MLS sync infrastructure lives in `/Users/markmini/Projects/prior-lake-ecosystem/PriorLake.RealEstate`. That repo has its own CLAUDE.md. Don't run sync commands from this repo.
