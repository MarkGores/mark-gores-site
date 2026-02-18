# markgores.com — Claude Code Build Instructions

## What This Is

A personal website for Mark Gores, a realtor in Prior Lake, Minnesota. This is NOT a lead-gen site. It's the site people land on when someone says "you should call Mark Gores" and they Google him. The goal: look like a real person, not a real estate template.

## Design Reference

The file `prototype.html` in this repo is the complete, approved design prototype. **Match this design exactly** — layout, colors, typography, spacing, content. It's a single-page scrolling site.

## Tech Stack

- **Hosting:** Vercel (Mark has a Pro account, repo is already connected)
- **Framework:** Keep it simple. Static HTML/CSS is fine. If you want a framework, Astro or Next.js static export. No heavy dependencies.
- **Domain:** markgores.com (will be pointed at Vercel)

## Design Specs (from the prototype)

### Color Palette
```css
--cream: #F5F0E8;       /* Background */
--dark: #1A1A18;        /* Dark sections, headings */
--warm: #8B7355;        /* Labels, accents */
--accent: #C4553A;      /* Terracotta — emphasis, hover */
--sage: #7A8B6F;        /* PLE card accent */
--light-warm: #E8DFD0;  /* Borders, subtle backgrounds */
--text: #2C2C28;        /* Body text */
--text-light: #6B6860;  /* Secondary text */
```

### Typography
- **Headlines:** DM Serif Display (Google Fonts)
- **Body:** Newsreader (Google Fonts)
- **Mono/Labels:** JetBrains Mono (Google Fonts)

### Key Design Details
- Subtle grain/noise texture overlay on the entire page
- Cream background, NOT white
- Dark section (#1A1A18) for the "How I Work" block — creates visual rhythm
- Warm beige section (#E8DFD0) for the personal/photo section
- Fade-up animations on hero elements (CSS only, staggered delays)
- Nav has backdrop-filter blur with semi-transparent cream background
- All sections smooth-scroll from nav links

## Page Sections (in scroll order)

1. **Nav** — Fixed top. "Mark Gores" left, section links right (How I Work, Proof, Local, Contact)
2. **Hero** — Big headline "I'm a realtor who will talk you *out of* a bad deal." with supporting text, stats row (22 years, 40 years in PL, 5.0 Zillow stars)
3. **How I Work** — Dark background section. Four cards in 2x2 grid: "I'll respond fast", "I won't hound you", "I know the deals", "I'll be honest"
4. **Testimonials** — Four review cards in 2x2 grid on cream background
5. **Community/PLE** — Two-column: story text left, PLE card right with sage green left border
6. **Personal** — Warm background. Two-column: bio text left, photos right (family photo main, pickleball photo secondary below it)
7. **Contact** — Centered. Phone and email, that's it.
8. **Footer** — Simple. Copyright + "Real estate without the pitch."

## Images

Two photos to include, place in `/public/images/`:

1. **family.jpg** — Family of four photo. Used as the main photo in the Personal section. Aspect ratio ~4:3, `object-fit: cover`, `object-position: center top`
2. **pickleball.jpg** — Pickleball medal photo. Secondary photo below the family photo. Aspect ratio ~3:4, `object-fit: cover`, `object-position: center top`

Mark will add these image files to the repo manually.

## Content Notes

- All copy is in the prototype HTML — use it verbatim
- The testimonial from "Bud, homebuyer" is real. The other three are placeholder examples based on real feedback themes — Mark should replace these with actual Zillow reviews
- The tagline "Real estate without the pitch." appears in the footer
- "Hand-built, not templated." was in the old version's footer — optional, could add back

## Important: What NOT to Do

- No stock photos. No house keys, no handshakes, no "SOLD" signs.
- No third-person bio ("Mark Gores is a dedicated real estate professional...")
- No lead capture forms, pop-ups, or "Schedule a FREE consultation!" CTAs
- No blog section (Mark doesn't want to maintain one)
- No MLS listing integration
- No heavy JavaScript frameworks or unnecessary dependencies
- No purple gradients, no Inter font, no generic AI-site aesthetics

## SEO Basics

- Title: "Mark Gores | Realtor in Prior Lake, Minnesota"
- Meta description: Something like "22 years of real estate experience in Prior Lake, MN. No pitch, no pressure — just honest advice."
- Use semantic HTML (h1, h2, section, nav, footer, etc.)
- Alt text on images
- Fast loading — no bloat

## Deployment

The existing repo is `mark-gores-site` on Vercel. Push to main branch and Vercel auto-deploys. The current preview URL is https://mark-gores-site.vercel.app/

## After Launch

Mark may want to:
- Add a "Living Here" section later (local neighborhood info bridging PLE → real estate)
- Possibly integrate a lead warming landing page
- These are future considerations, not part of this build
