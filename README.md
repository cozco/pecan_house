# The Pecan House

Static marketing site for The Pecan House — a 6-bedroom historic stay and furnished corporate housing option in Texarkana with a separate carriage house apartment. The site's job is to feel polished, support corporate and extended-stay inquiries, and funnel visitors to the waitlist or full-property booking links.

## Stack

- Plain HTML, CSS, and a few lines of vanilla JS — no build step, no framework.
- Hosted on **Cloudflare Pages** (free tier, global CDN, free TLS).
- Domain registered through **Cloudflare Registrar** (at-cost, no markup).

Total run rate: ~$10/year for the domain. $0 for hosting.

## Files

```
index.html      — the homepage
waitlist.html   — waitlist intake page
corporate-housing.html — corporate housing detail page
styles.css      — all styling
script.js       — mobile nav toggle, footer year, and inquiry mailto handoffs
_headers        — Cloudflare Pages caching + security headers
images/         — public web assets copied/optimized from the renovation design folder
```

## Local preview

No build step needed. Just open `index.html` in a browser, or run a tiny local server:

```bash
cd pecan_house
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Updating the listing links

The main Airbnb and Vrbo links currently point to the platform homepages (`https://www.airbnb.com/` and `https://www.vrbo.com/`) so click behavior can be tested. Replace those full-property links with the real listing URLs once they go live.

Room-level Airbnb and Vrbo buttons were intentionally removed. Add them back later only if the room-by-room listing strategy is ready.

The public contact email is `stay@pecanhousetexarkana.info`.

## Google Forms waitlist embed

The waitlist page embeds a Google Form at:

```text
https://docs.google.com/forms/d/e/1FAIpQLSf54U15VihP3Bj6ZIxUmPtioRNlTGcKq2YoYhOXcP3NPmNEhQ/viewform?embedded=true
```

If the form changes, replace the iframe `src` in `waitlist.html` with the new Google Forms embed URL.

## Adding photos

Final photos aren't published yet, so the site uses approved renderings and brand mockups as intentional placeholders. The page states this visibly. When the renovation is photographed:

1. Drop images into `images/` (see `images/README.txt` for filenames and sizing).
2. Open `styles.css`, find the `.room-photo[data-room="..."]` selectors, and replace each rendering background with `background-image: url('images/<filename>.jpg')`.
3. For the hero, replace the `.hero-media` background image URL with the final exterior photo.

## Deploying to Cloudflare Pages

### One-time setup

1. Push this directory to a GitHub repo (private is fine).
2. Sign in to [Cloudflare Dashboard](https://dash.cloudflare.com) → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**.
3. Pick the repo. Build settings:
   - **Framework preset:** None
   - **Build command:** *(leave empty)*
   - **Build output directory:** `/`
4. Click **Save and Deploy**. First deploy takes ~30 seconds. You'll get a `*.pages.dev` URL.

### Custom domain

1. In Cloudflare Dashboard → **Domain Registration** → **Register Domains**, buy `thepecanhouse.com` (or whatever you choose). Cloudflare charges at-cost — no upsells.
2. After registration, the domain is automatically on Cloudflare DNS.
3. Back in your Pages project → **Custom domains** → **Set up a custom domain**. Enter the domain. Cloudflare wires up DNS and TLS for you.
4. Done. Site is live at the custom domain with HTTPS, behind Cloudflare's CDN.

### Subsequent updates

Push to the connected branch (usually `main`). Cloudflare Pages auto-deploys on every push. Rollback to any prior deployment in one click from the Pages dashboard.

## Editing copy

All visible text lives in `index.html`. Search for the section you want to change (e.g. `id="about"`, `id="rooms"`) and edit in place. Save, refresh, done.

## Notes

- The favicon uses `images/brand/pecan-house-favicon.png`.
- Fonts come from Google Fonts (Cormorant Garamond + Lora). They're preconnected for fast load. If you ever want to fully self-host them for privacy, download the WOFF2 files into `images/fonts/` and swap the `<link>` for an `@font-face` block.
- The `_headers` file enables long cache lifetimes on assets and adds a few sensible security headers. Cloudflare Pages picks it up automatically — no config needed.
