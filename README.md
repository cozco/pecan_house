# The Pecan House

Single-page marketing site for The Pecan House — a 6-bedroom historic stay in Texarkana with a separate carriage house apartment. The site's job is to feel polished, preserve the approved property copy, and funnel visitors to the Airbnb and Vrbo listings.

## Stack

- Plain HTML, CSS, and a few lines of vanilla JS — no build step, no framework.
- Hosted on **Cloudflare Pages** (free tier, global CDN, free TLS).
- Domain registered through **Cloudflare Registrar** (at-cost, no markup).

Total run rate: ~$10/year for the domain. $0 for hosting.

## Files

```
index.html      — the page itself
styles.css      — all styling
script.js       — mobile nav toggle, footer year, and corporate inquiry mailto handoff
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

Each room also has its own pair of placeholders, such as `[ROYAL_ROOM_AIRBNB_URL]`, `[ROYAL_ROOM_VRBO_URL]`, and `[CARRIAGE_HOUSE_AIRBNB_URL]`. Replace those with the individual room listing URLs when they are ready.

The public contact email is `stay@pecanhousetexarkana.info`.

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
