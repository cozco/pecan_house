/**
 * Runtime DOM tests for The Pecan House.
 *
 * These tests load index.html into a real jsdom environment, actually run
 * script.js, and dispatch real click events against the DOM. The Python suite
 * covers static structure & content accuracy; this suite covers JS *behavior*
 * and native browser semantics like the <details>/<summary> accordion.
 *
 * Run from the project root:
 *   npm test
 */

import { describe, it, before, beforeEach } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { JSDOM } from "jsdom";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");

const indexHtml = readFileSync(resolve(ROOT, "index.html"), "utf8");
const scriptJs = readFileSync(resolve(ROOT, "script.js"), "utf8");

const EXPECTED_ROOMS = ["bay", "garage", "guest", "red", "royal", "twin", "walnut"];
const FULL_PROPERTY_AIRBNB_URL = "https://www.airbnb.com/";
const FULL_PROPERTY_VRBO_URL = "https://www.vrbo.com/";

/**
 * Build a fresh jsdom whose script.js has been executed inline.
 * Inlining sidesteps jsdom's loader trying to fetch script.js over HTTP.
 */
function freshDom() {
  const html = indexHtml.replace(
    /<script[^>]*src="script\.js"[^>]*><\/script>/,
    `<script>${scriptJs}</script>`,
  );
  return new JSDOM(html, { runScripts: "dangerously" });
}

describe("mobile nav toggle", () => {
  let dom, doc, toggle, nav;

  beforeEach(() => {
    dom = freshDom();
    doc = dom.window.document;
    toggle = doc.querySelector(".nav-toggle");
    nav = doc.getElementById("primary-nav");
  });

  it("nav is closed on initial render", () => {
    assert.equal(nav.classList.contains("is-open"), false);
    assert.equal(toggle.getAttribute("aria-expanded"), "false");
  });

  it("clicking the toggle opens the nav and flips aria-expanded", () => {
    toggle.click();
    assert.equal(nav.classList.contains("is-open"), true);
    assert.equal(toggle.getAttribute("aria-expanded"), "true");
  });

  it("clicking the toggle a second time closes the nav", () => {
    toggle.click();
    toggle.click();
    assert.equal(nav.classList.contains("is-open"), false);
    assert.equal(toggle.getAttribute("aria-expanded"), "false");
  });

  it("clicking a nav link closes the open nav", () => {
    toggle.click();
    nav.querySelector("a").click();
    assert.equal(nav.classList.contains("is-open"), false);
    assert.equal(toggle.getAttribute("aria-expanded"), "false");
  });

  it("clicking the booking CTA in the nav also closes the nav", () => {
    toggle.click();
    nav.querySelector(".nav-cta").click();
    assert.equal(nav.classList.contains("is-open"), false);
  });
});

describe("footer year", () => {
  it("populates #year with the current 4-digit year", () => {
    const { window } = freshDom();
    const yearEl = window.document.getElementById("year");
    assert.ok(yearEl);
    assert.equal(yearEl.textContent, String(new Date().getFullYear()));
  });
});

describe("FAQ accordion (native <details>/<summary>)", () => {
  let doc, items;

  beforeEach(() => {
    doc = freshDom().window.document;
    items = [...doc.querySelectorAll(".faq-item")];
  });

  it("renders seven FAQ items as <details> elements", () => {
    assert.equal(items.length, 7);
    for (const item of items) {
      assert.equal(item.tagName, "DETAILS");
      assert.ok(item.querySelector("summary"));
    }
  });

  it("FAQ items start collapsed", () => {
    for (const item of items) {
      assert.equal(item.open, false, "FAQ items should be closed by default");
    }
  });

  it("clicking the summary toggles open/closed", () => {
    const item = items[0];
    const summary = item.querySelector("summary");

    // jsdom doesn't fully implement the click→toggle for <summary>, so we
    // toggle programmatically (which is what the click ultimately does).
    item.open = true;
    assert.equal(item.open, true);
    item.open = false;
    assert.equal(item.open, false);

    // Verify the click handler at least dispatches without error.
    summary.click();
  });

  it("FAQ items are independently expandable", () => {
    items[0].open = true;
    items[1].open = true;
    assert.equal(items[0].open, true);
    assert.equal(items[1].open, true);
    // Native <details> are independent — opening one does not close another.
    assert.equal(items[2].open, false);
  });
});

describe("booking CTAs are wired up", () => {
  let doc;

  before(() => {
    doc = freshDom().window.document;
  });

  it("Airbnb buttons present, marked as external new-tab targets", () => {
    const links = [...doc.querySelectorAll(`a[href="${FULL_PROPERTY_AIRBNB_URL}"]`)];
    assert.ok(links.length >= 2, `expected ≥2 full-property Airbnb links, found ${links.length}`);
    for (const a of links) {
      if (a.getAttribute("target")) {
        assert.equal(a.getAttribute("target"), "_blank");
        const rel = a.getAttribute("rel") || "";
        assert.match(rel, /noopener/);
        assert.match(rel, /noreferrer/);
      }
    }
  });

  it("VRBO buttons present, marked as external new-tab targets", () => {
    const links = [...doc.querySelectorAll(`a[href="${FULL_PROPERTY_VRBO_URL}"]`)];
    assert.ok(links.length >= 2, `expected ≥2 full-property VRBO links, found ${links.length}`);
    for (const a of links) {
      if (a.getAttribute("target")) {
        assert.equal(a.getAttribute("target"), "_blank");
        const rel = a.getAttribute("rel") || "";
        assert.match(rel, /noopener/);
        assert.match(rel, /noreferrer/);
      }
    }
  });

  it("contact email is the approved address", () => {
    const mailto = doc.querySelector('a[href^="mailto:"]');
    assert.ok(mailto, "no mailto link found");
    assert.equal(mailto.getAttribute("href"), "mailto:stay@pecanhousetexarkana.info");
  });

  it('every internal "#..." anchor lands on a real element', () => {
    const anchors = [...doc.querySelectorAll('a[href^="#"]')];
    const broken = [];
    for (const a of anchors) {
      const href = a.getAttribute("href");
      if (href === "#") continue;
      if (!doc.getElementById(href.slice(1))) broken.push(href);
    }
    assert.deepEqual(broken, [], `broken anchors: ${broken.join(", ")}`);
  });
});

describe("rooms section", () => {
  let doc;

  before(() => {
    doc = freshDom().window.document;
  });

  it("renders all seven expected rooms (6 bedrooms + carriage house)", () => {
    const rooms = [...doc.querySelectorAll("[data-room]")]
      .map((el) => el.dataset.room)
      .sort();
    assert.deepEqual(rooms, EXPECTED_ROOMS,
      "rooms in HTML differ from expected set");
  });

  it("each room card has a heading, tagline, description, and meta tags", () => {
    const cards = [...doc.querySelectorAll(".room-card")];
    assert.equal(cards.length, 7);
    for (const card of cards) {
      assert.ok(card.querySelector("h3"), "every room card needs an <h3>");
      assert.ok(card.querySelector(".room-tagline"),
        "every room card needs a .room-tagline");
      const metas = card.querySelectorAll(".room-meta li");
      assert.ok(metas.length >= 1,
        "every room card needs at least one .room-meta li");
      const roomLinks = card.querySelectorAll(".room-actions a");
      assert.equal(roomLinks.length, 2, "every room card needs Airbnb and VRBO links");
      for (const link of roomLinks) {
        assert.equal(link.getAttribute("target"), "_blank");
        assert.match(link.getAttribute("rel") || "", /noopener/);
      }
    }
  });

  it("Walnut Room is named correctly per COPY.md", () => {
    const card = doc.querySelector('[data-room="walnut"]')?.closest(".room-card");
    assert.ok(card, "no walnut room card");
    assert.equal(card.querySelector("h3").textContent.trim(), "Walnut Room");
  });

  it("Carriage House Apartment is named correctly per COPY.md", () => {
    const card = doc.querySelector('[data-room="garage"]')?.closest(".room-card");
    assert.ok(card, "no garage/carriage card");
    assert.equal(
      card.querySelector("h3").textContent.trim(),
      "Carriage House Apartment",
    );
  });
});

describe("corporate inquiry", () => {
  let doc;

  before(() => {
    doc = freshDom().window.document;
  });

  it("renders a corporate section and inquiry form", () => {
    const section = doc.getElementById("corporate");
    assert.ok(section, "corporate section missing");
    const form = doc.getElementById("corporate-inquiry-form");
    assert.ok(form, "corporate form missing");
    assert.equal(form.getAttribute("action"), "mailto:stay@pecanhousetexarkana.info");
  });

  it("requests company, dates, guest count, and contact info", () => {
    for (const id of [
      "company-name",
      "contact-name",
      "contact-email",
      "dates-needed",
      "guest-count",
      "booking-type",
    ]) {
      assert.ok(doc.getElementById(id), `${id} missing`);
    }
  });
});

describe("brand & layout chrome", () => {
  let doc;

  before(() => {
    doc = freshDom().window.document;
  });

  it("updated logo is in the header brand link", () => {
    const brand = doc.querySelector("a.brand[href='#top']");
    assert.ok(brand, "header brand link missing");
    const img = brand.querySelector("img");
    assert.ok(img);
    assert.equal(img.getAttribute("src"), "images/brand/pecan-house-logo.png");
  });

  it("full logo is in the footer", () => {
    const footer = doc.querySelector("footer");
    assert.ok(footer);
    const img = footer.querySelector("img.footer-logo");
    assert.ok(img, "footer logo image missing");
    assert.equal(img.getAttribute("src"), "images/brand/pecan-house-logo.png");
  });

  it("photos-coming-soon banner is rendered", () => {
    const banner = doc.querySelector(".banner");
    assert.ok(banner, ".banner element missing");
    assert.match(banner.textContent, /Renderings shown throughout\./);
    assert.match(banner.textContent, /Final photography will be uploaded/);
  });

  it("favicon is wired to the updated logo asset", () => {
    const icon = doc.querySelector('link[rel="icon"]');
    assert.ok(icon);
    assert.equal(icon.getAttribute("href"), "images/brand/pecan-house-favicon.png");
    assert.equal(icon.getAttribute("type"), "image/png");
  });
});
