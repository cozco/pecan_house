"""
Test suite for The Pecan House static site.

Run from the project root:
    python3 -m unittest tests.test_site -v
or:
    python3 tests/test_site.py

Uses only the Python standard library so it runs anywhere python3 is installed.
"""

from __future__ import annotations

import os
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
WAITLIST = ROOT / "waitlist.html"
CORPORATE_HOUSING = ROOT / "corporate-housing.html"
STYLES = ROOT / "styles.css"
SCRIPT = ROOT / "script.js"
HEADERS = ROOT / "_headers"
README = ROOT / "README.md"
COPY = ROOT / "COPY.md"
BRAND_LOGO = ROOT / "images" / "brand" / "pecan-house-logo.png"
BRAND_FAVICON = ROOT / "images" / "brand" / "pecan-house-favicon.png"
IMAGES = ROOT / "images"

EXPECTED_ROOMS = {"royal", "red", "bay", "guest", "twin", "walnut", "garage"}
EXPECTED_ROOM_SVGS = {
    "exterior-hero.svg",
    "royal-room.svg",
    "red-room.svg",
    "bay-room.svg",
    "guest-room.svg",
    "twin-room.svg",
    "walnut-room.svg",
    "garage-apt.svg",
}
EXPECTED_BRAND_ASSETS = {
    "pecan-house-logo.png",
    "pecan-house-favicon.png",
    "robe-embroidery.jpg",
    "robe-slippers-embroidery.jpg",
    "red-room-bedroom-rendering.jpg",
    "royal-room-rendering.jpg",
    "royal-bath-rendering.jpg",
    "oak-suite-rendering.jpg",
    "pecan-bath-rendering.jpg",
    "parlor-rendering.jpg",
    "carriage-house-rendering.jpg",
    "twin-room-bedroom-rendering.jpg",
    "walnut-room-bedroom-rendering.jpg",
}
PUBLIC_EMAIL = "stay@pecanhousetexarkana.info"
FULL_PROPERTY_AIRBNB_URL = "https://www.airbnb.com/"
FULL_PROPERTY_VRBO_URL = "https://www.vrbo.com/"
# Optional local-only guard. Set PRIVATE_STREET_ADDRESS before running tests if
# you want to verify a private address never appears in public HTML.
PRIVATE_STREET_ADDRESS = os.environ.get("PRIVATE_STREET_ADDRESS")


# ───────────────────────── HTML parsing helper ───────────────────────── #

class _Collector(HTMLParser):
    """Walks the HTML, recording every tag with its attributes and a depth."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.elements: list[dict] = []
        self.errors: list[str] = []
        self.text_parts: list[str] = []
        self._depth = 0
        self._open_stack: list[str] = []

    def handle_starttag(self, tag, attrs):
        attr_dict = {k: (v if v is not None else "") for k, v in attrs}
        self.elements.append({"tag": tag, "attrs": attr_dict, "depth": self._depth})
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img",
                       "input", "link", "meta", "param", "source", "track", "wbr"}:
            self._open_stack.append(tag)
            self._depth += 1

    def handle_startendtag(self, tag, attrs):
        attr_dict = {k: (v if v is not None else "") for k, v in attrs}
        self.elements.append({"tag": tag, "attrs": attr_dict, "depth": self._depth})

    def handle_endtag(self, tag):
        if self._open_stack and self._open_stack[-1] == tag:
            self._open_stack.pop()
            self._depth -= 1
        else:
            self.errors.append(f"close <{tag}> without matching open")

    def handle_data(self, data):
        self.text_parts.append(data)


def parse(html: str) -> _Collector:
    c = _Collector()
    c.feed(html)
    return c


# ─────────────────────────── File presence ──────────────────────────── #

class TestFilesExist(unittest.TestCase):
    def test_index_exists(self):
        self.assertTrue(INDEX.is_file())

    def test_waitlist_exists(self):
        self.assertTrue(WAITLIST.is_file())

    def test_corporate_housing_exists(self):
        self.assertTrue(CORPORATE_HOUSING.is_file())

    def test_styles_exists(self):
        self.assertTrue(STYLES.is_file())

    def test_script_exists(self):
        self.assertTrue(SCRIPT.is_file())

    def test_headers_exists(self):
        self.assertTrue(HEADERS.is_file())

    def test_readme_exists(self):
        self.assertTrue(README.is_file())

    def test_images_dir_exists(self):
        self.assertTrue(IMAGES.is_dir())

    def test_copy_md_exists(self):
        self.assertTrue(COPY.is_file(), "COPY.md (the approved copy reference) missing")

    def test_logo_files_exist(self):
        self.assertTrue(BRAND_LOGO.is_file(), "brand logo PNG missing")
        self.assertTrue(BRAND_FAVICON.is_file(), "brand favicon PNG missing")

    def test_room_svgs_present(self):
        present = {p.name for p in IMAGES.glob("*.svg")}
        missing = EXPECTED_ROOM_SVGS - present
        self.assertEqual(missing, set(), f"missing room SVGs: {missing}")

    def test_brand_assets_present(self):
        present = {p.name for p in (IMAGES / "brand").glob("*")}
        missing = EXPECTED_BRAND_ASSETS - present
        self.assertEqual(missing, set(), f"missing brand/design assets: {missing}")


# ─────────────────────────── HTML structure ─────────────────────────── #

class TestHtmlStructure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX.read_text(encoding="utf-8")
        cls.doc = parse(cls.html)

    def test_doctype_present(self):
        self.assertRegex(self.html[:100].lower(), r"<!doctype html>")

    def test_lang_attribute(self):
        html_tags = [e for e in self.doc.elements if e["tag"] == "html"]
        self.assertEqual(len(html_tags), 1)
        self.assertEqual(html_tags[0]["attrs"].get("lang"), "en")

    def test_no_misnested_tags(self):
        self.assertEqual(self.doc.errors, [], f"misnested HTML: {self.doc.errors}")

    def test_single_h1(self):
        h1s = [e for e in self.doc.elements if e["tag"] == "h1"]
        self.assertEqual(len(h1s), 1)

    def test_meta_charset(self):
        metas = [e for e in self.doc.elements if e["tag"] == "meta"]
        self.assertTrue(
            any(m["attrs"].get("charset", "").lower() == "utf-8" for m in metas)
        )

    def test_meta_viewport(self):
        metas = [e for e in self.doc.elements if e["tag"] == "meta"]
        viewports = [m for m in metas if m["attrs"].get("name") == "viewport"]
        self.assertEqual(len(viewports), 1)
        self.assertIn("width=device-width", viewports[0]["attrs"].get("content", ""))

    def test_title_uses_approved_copy(self):
        self.assertIn(
            "<title>The Pecan House — Luxury Corporate Housing in Texarkana, AR</title>",
            self.html,
        )

    def test_meta_description_uses_approved_copy(self):
        metas = [e for e in self.doc.elements if e["tag"] == "meta"]
        descs = [m for m in metas if m["attrs"].get("name") == "description"]
        self.assertEqual(len(descs), 1)
        content = descs[0]["attrs"].get("content", "")
        self.assertIn("Luxury corporate housing in Texarkana", content)
        self.assertIn("flexible monthly stays", content)

    def test_open_graph_uses_approved_copy(self):
        metas = [e for e in self.doc.elements if e["tag"] == "meta"]
        og = {m["attrs"].get("property"): m["attrs"].get("content", "")
              for m in metas if m["attrs"].get("property", "").startswith("og:")}
        self.assertEqual(og.get("og:title"), "The Pecan House · Corporate Housing in Texarkana")
        self.assertIn("Fully furnished private suites", og.get("og:description", ""))

    def test_og_image_points_to_brand_jpeg(self):
        metas = [e for e in self.doc.elements if e["tag"] == "meta"]
        og_image = [m for m in metas if m["attrs"].get("property") == "og:image"]
        self.assertEqual(len(og_image), 1)
        self.assertEqual(og_image[0]["attrs"]["content"], "images/brand/robe-embroidery.jpg")

    def test_favicon_uses_logo_mark(self):
        links = [e for e in self.doc.elements
                 if e["tag"] == "link" and e["attrs"].get("rel") == "icon"]
        self.assertEqual(len(links), 1, "expected exactly one favicon <link>")
        self.assertEqual(links[0]["attrs"].get("type"), "image/png")
        self.assertEqual(links[0]["attrs"].get("href"), "images/brand/pecan-house-favicon.png")

    def test_brand_fonts_loaded(self):
        # Cormorant Garamond for headlines, Lora for body.
        font_links = [e for e in self.doc.elements
                      if e["tag"] == "link"
                      and "fonts.googleapis.com" in e["attrs"].get("href", "")]
        combined = " ".join(l["attrs"]["href"] for l in font_links)
        self.assertIn("Cormorant+Garamond", combined,
                      "Cormorant Garamond not loaded from Google Fonts")
        self.assertIn("Lora", combined, "Lora not loaded from Google Fonts")


# ───────────────────────── Section anchors ──────────────────────────── #

class TestAnchors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = parse(INDEX.read_text(encoding="utf-8"))
        cls.ids = {e["attrs"].get("id") for e in cls.doc.elements if e["attrs"].get("id")}

    def test_required_sections_present(self):
        for required in ("top", "about", "space", "rooms", "amenities", "location", "who-stays", "corporate", "faq", "book"):
            self.assertIn(required, self.ids, f"section id='{required}' missing")

    def test_internal_anchors_resolve(self):
        anchors = [e for e in self.doc.elements
                   if e["tag"] == "a" and e["attrs"].get("href", "").startswith("#")]
        missing = []
        for a in anchors:
            href = a["attrs"]["href"]
            if href == "#":
                continue
            target = href[1:]
            if target and target not in self.ids:
                missing.append(href)
        self.assertEqual(missing, [], f"broken anchors: {missing}")

    def test_aria_controls_targets_exist(self):
        for el in (e for e in self.doc.elements if e["attrs"].get("aria-controls")):
            target = el["attrs"]["aria-controls"]
            self.assertIn(target, self.ids,
                          f"aria-controls='{target}' has no matching id")


# ───────────────────────── Booking buttons ──────────────────────────── #

class TestBookingButtons(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = parse(INDEX.read_text(encoding="utf-8"))
        cls.airbnb_links = [
            e for e in cls.doc.elements
            if e["tag"] == "a" and e["attrs"].get("href") == FULL_PROPERTY_AIRBNB_URL
        ]
        cls.vrbo_links = [
            e for e in cls.doc.elements
            if e["tag"] == "a" and e["attrs"].get("href") == FULL_PROPERTY_VRBO_URL
        ]

    def test_airbnb_homepage_placeholder_present(self):
        # Hero CTA, lower booking CTA, footer = at least 2; with footer makes 3.
        self.assertGreaterEqual(len(self.airbnb_links), 2,
                                "expected at least 2 full-property Airbnb homepage links")

    def test_vrbo_homepage_placeholder_present(self):
        self.assertGreaterEqual(len(self.vrbo_links), 2,
                                "expected at least 2 full-property VRBO homepage links")

    def test_external_links_open_new_tab(self):
        for a in self.airbnb_links + self.vrbo_links:
            self.assertEqual(a["attrs"].get("target"), "_blank",
                             "booking link missing target='_blank'")

    def test_external_links_have_secure_rel(self):
        for a in self.airbnb_links + self.vrbo_links:
            rel = a["attrs"].get("rel", "")
            self.assertIn("noopener", rel)
            self.assertIn("noreferrer", rel)

    def test_button_copy_matches_approved(self):
        text = INDEX.read_text(encoding="utf-8")
        # Hero buttons now prioritize corporate housing and the waitlist.
        self.assertIn(">Join Our Waitlist<", text)
        self.assertIn(">Corporate Housing<", text)
        # Lower section keeps full-property platform links.
        self.assertIn(">View Entire Space on Airbnb<", text)
        self.assertIn(">View Entire Space on VRBO<", text)


# ──────────────────────────── Rooms grid ────────────────────────────── #

class TestRooms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX.read_text(encoding="utf-8")
        cls.css = STYLES.read_text(encoding="utf-8")
        cls.doc = parse(cls.html)
        cls.room_values = {
            e["attrs"]["data-room"]
            for e in cls.doc.elements
            if "data-room" in e["attrs"]
        }

    def test_seven_rooms_in_html(self):
        self.assertEqual(self.room_values, EXPECTED_ROOMS,
                         f"rooms differ from expected: {self.room_values ^ EXPECTED_ROOMS}")

    def test_each_room_has_css_rule(self):
        for room in self.room_values:
            self.assertRegex(self.css, rf'\.room-photo\[data-room="{room}"\]\s*\{{',
                             f"no CSS rule for [data-room='{room}']")

    def test_each_room_uses_local_image_background(self):
        for room in self.room_values:
            pattern = rf'\.room-photo\[data-room="{room}"\][^{{]*\{{[^}}]*url\([\'"]?images/[^\'")]+\.(?:svg|png|jpe?g|webp)[\'"]?\)'
            self.assertRegex(self.css, pattern,
                             f"data-room='{room}' should use a local image background")

    def test_no_orphan_css_rooms(self):
        css_rooms = set(re.findall(r'\.room-photo\[data-room="([^"]+)"\]', self.css))
        orphans = css_rooms - self.room_values
        self.assertEqual(orphans, set(), f"orphan CSS rooms: {orphans}")

    def test_updated_room_placeholders_are_bedrooms(self):
        expected = {
            "red": "images/brand/red-room-bedroom-rendering.jpg",
            "twin": "images/brand/twin-room-bedroom-rendering.jpg",
            "walnut": "images/brand/walnut-room-bedroom-rendering.jpg",
        }
        for room, path in expected.items():
            pattern = rf'\.room-photo\[data-room="{room}"\]\s*\{{[^}}]*url\([\'"]?{re.escape(path)}[\'"]?\)'
            self.assertRegex(self.css, pattern,
                             f"{room} should use the new bedroom placeholder")
        for old_path in (
            "robe-slippers-embroidery.jpg",
            "royal-bath-rendering.jpg",
            "pecan-bath-rendering.jpg",
        ):
            self.assertNotRegex(
                self.css,
                rf'\.room-photo\[data-room="(?:red|twin|walnut)"\]\s*\{{[^}}]*{re.escape(old_path)}',
                f"{old_path} should not be used for Red, Twin, or Walnut",
            )

    def test_walnut_room_named_correctly(self):
        # Per COPY.md, the sixth bedroom is the Walnut Room.
        self.assertIn("walnut", self.room_values, "walnut room missing from HTML")
        self.assertIn(">Walnut Room<", self.html, "Walnut Room title missing")

    def test_carriage_house_named_correctly(self):
        self.assertIn(">Carriage House Apartment<", self.html,
                      "Carriage House Apartment title missing")

    def test_room_booking_buttons_removed(self):
        self.assertNotIn("room-actions", self.html)
        self.assertNotIn("btn-room", self.html)
        self.assertNotIn("_ROOM_AIRBNB_URL", self.html)
        self.assertNotIn("_ROOM_VRBO_URL", self.html)
        self.assertNotIn("CARRIAGE_HOUSE_AIRBNB_URL", self.html)
        self.assertNotIn("CARRIAGE_HOUSE_VRBO_URL", self.html)


# ───────────────────── Corporate inquiry form ──────────────────────── #

class TestCorporateInquiry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX.read_text(encoding="utf-8")
        cls.css = STYLES.read_text(encoding="utf-8")
        cls.js = SCRIPT.read_text(encoding="utf-8")
        cls.doc = parse(cls.html)

    def test_corporate_section_exists(self):
        ids = {e["attrs"].get("id") for e in self.doc.elements}
        self.assertIn("corporate", ids, "no #corporate section")
        self.assertIn("Corporate Housing", self.html)
        self.assertIn("Private suites and whole-house stays", self.html)

    def test_corporate_form_targets_public_email(self):
        forms = [e for e in self.doc.elements if e["tag"] == "form"]
        corporate_forms = [
            f for f in forms
            if f["attrs"].get("id") == "corporate-inquiry-form"
        ]
        self.assertEqual(len(corporate_forms), 1, "expected one corporate inquiry form")
        self.assertEqual(
            corporate_forms[0]["attrs"].get("action"),
            f"mailto:{PUBLIC_EMAIL}",
        )

    def test_corporate_form_requests_required_information(self):
        for field_id in (
            "company-name",
            "contact-name",
            "contact-email",
            "dates-needed",
            "guest-count",
            "booking-type",
            "corporate-notes",
        ):
            self.assertIn(f'id="{field_id}"', self.html, f"{field_id} missing")

    def test_corporate_form_mailto_script_present(self):
        self.assertIn("corporate-inquiry-form", self.js)
        self.assertIn(f"mailto:{PUBLIC_EMAIL}?subject=", self.js)
        self.assertIn("Corporate Inquiry - The Pecan House", self.js)

    def test_corporate_section_has_dark_split_styling(self):
        self.assertRegex(self.css, r"\.corporate\s*\{[^}]*var\(--color-text\)",
                         "corporate section should use the dark brand surface")
        self.assertRegex(self.css, r"\.corporate-grid\s*\{[^}]*display:\s*grid",
                         "corporate layout should be a split grid")


# ───────────────────── Corporate housing content ───────────────────── #

class TestCorporateHousingContent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX.read_text(encoding="utf-8")
        cls.css = STYLES.read_text(encoding="utf-8")
        cls.doc = parse(cls.html)

    def test_homepage_hero_prioritizes_corporate_housing(self):
        self.assertIn("Luxury Corporate Housing in Texarkana", self.html)
        self.assertIn("Fully furnished private suites for traveling professionals", self.html)
        for phrase in (
            "Utilities included",
            "Fast Wi-Fi",
            "Private baths available",
            "Flexible monthly stays",
            "Minutes from downtown and major employers",
        ):
            self.assertIn(phrase, self.html)

    def test_waitlist_cta_links_to_page(self):
        self.assertIn('href="waitlist.html"', self.html)
        self.assertIn(">Join Our Waitlist<", self.html)

    def test_nearby_employers_replace_long_distance_drive_time(self):
        for employer in (
            "CHRISTUS St. Michael Health System",
            "Wadley Regional Medical Center",
            "Red River Army Depot",
            "Cooper Tire",
            "Texarkana Regional Airport",
        ):
            self.assertIn(employer, self.html)
        self.assertNotIn("Dallas, Shreveport", self.html)
        self.assertNotIn("Little Rock", self.html)

    def test_who_stays_here_section_exists(self):
        ids = {e["attrs"].get("id") for e in self.doc.elements}
        self.assertIn("who-stays", ids)
        for guest_type in (
            "Traveling Medical Staff",
            "Construction Managers",
            "Remote Workers",
            "Visiting Faculty",
            "Corporate Relocations",
            "Family Gatherings",
        ):
            self.assertIn(guest_type, self.html)

    def test_new_section_styles_exist(self):
        for selector in (".hero-support", ".stay-grid", ".stay-card", ".corporate-points"):
            self.assertIn(selector, self.css)


# ───────────────────────── New standalone pages ────────────────────── #

class TestStandalonePages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.waitlist_html = WAITLIST.read_text(encoding="utf-8")
        cls.corporate_html = CORPORATE_HOUSING.read_text(encoding="utf-8")
        cls.css = STYLES.read_text(encoding="utf-8")

    def test_waitlist_page_has_matching_brand_chrome(self):
        for html in (self.waitlist_html, self.corporate_html):
            self.assertIn('src="images/brand/pecan-house-logo.png"', html)
            self.assertIn('href="styles.css"', html)
            self.assertIn('src="script.js"', html)
            self.assertIn('href="index.html#about"', html)
            self.assertIn('href="waitlist.html"', html)
            self.assertIn('href="corporate-housing.html"', html)

    def test_waitlist_embeds_google_form(self):
        self.assertIn("google-form-shell", self.waitlist_html)
        self.assertIn(
            "https://docs.google.com/forms/d/e/1FAIpQLSf54U15VihP3Bj6ZIxUmPtioRNlTGcKq2YoYhOXcP3NPmNEhQ/viewform?embedded=true",
            self.waitlist_html,
        )
        self.assertIn('title="The Pecan House waitlist request form"', self.waitlist_html)

    def test_corporate_housing_page_has_requested_sections(self):
        for phrase in (
            "Perfect For",
            "Traveling Nurses",
            "Plant Shutdown Contractors",
            "Government Contractors",
            "Professors",
            "Engineers",
            "Insurance Adjusters",
            "Benefits",
            "Entire-house rentals",
            "Individual room rentals",
            "Monthly invoicing",
            "Flexible terms",
            "High-speed Wi-Fi",
            "Fully furnished",
        ):
            self.assertIn(phrase, self.corporate_html)

    def test_subpage_styles_exist(self):
        for selector in (
            ".page-hero",
            ".waitlist-layout",
            ".google-form-shell",
            ".corporate-page-grid",
            ".feature-panel-grid",
            ".benefit-grid",
        ):
            self.assertIn(selector, self.css)


# ──────────────────────── Banner & FAQ ──────────────────────────────── #

class TestBanner(unittest.TestCase):
    def test_photos_coming_soon_banner_present(self):
        html = INDEX.read_text(encoding="utf-8")
        self.assertIn("Renderings shown throughout.", html)
        self.assertIn("Final photography will be uploaded when renovation is complete.", html)

    def test_banner_has_class(self):
        doc = parse(INDEX.read_text(encoding="utf-8"))
        self.assertTrue(
            any("banner" in e["attrs"].get("class", "").split() for e in doc.elements),
            "no element has class='banner'",
        )

    def test_banner_styled_with_brand_tokens(self):
        css = STYLES.read_text(encoding="utf-8")
        self.assertRegex(css, r"\.banner\s*\{[^}]*var\(--color-text\)",
                         "banner background should use --color-text")


class TestFaq(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX.read_text(encoding="utf-8")
        cls.doc = parse(cls.html)

    def test_faq_section_exists(self):
        ids = {e["attrs"].get("id") for e in self.doc.elements}
        self.assertIn("faq", ids, "no #faq section")

    def test_eight_faq_details_blocks(self):
        details = [e for e in self.doc.elements if e["tag"] == "details"]
        self.assertEqual(len(details), 8, f"expected 8 FAQ items, found {len(details)}")

    def test_each_details_has_summary(self):
        # Native accordion behavior requires each <details> to have a <summary>.
        # This is a structural sanity check via regex on the source.
        pattern = re.compile(r"<details\b[^>]*>\s*<summary\b", re.IGNORECASE)
        matches = pattern.findall(self.html)
        self.assertEqual(len(matches), 8, "every <details> should open with a <summary>")

    def test_faq_questions_match_copy(self):
        for question in (
            "When is check-in and check-out?",
            "How many guests can the house sleep?",
            "Is parking available?",
            "Are pets allowed?",
            "Can the carriage house apartment be booked separately?",
            "Do you support corporate bookings or custom rates?",
            "How do I join the waitlist?",
            "What's the cancellation policy?",
        ):
            self.assertIn(question, self.html, f"FAQ missing: {question}")


# ────────────────────── Logo placement & wiring ─────────────────────── #

class TestLogos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX.read_text(encoding="utf-8")
        cls.doc = parse(cls.html)

    def test_logo_mark_in_header(self):
        # Brand link in the header should embed the updated PNG logo.
        self.assertRegex(
            self.html,
            r'<a\s+href="#top"[^>]*class="brand"[^>]*>\s*<img\s+src="images/brand/pecan-house-logo\.png"',
            "updated PNG logo not present in the header brand link",
        )

    def test_full_logo_in_footer(self):
        # The updated PNG logo should appear inside the footer.
        footer_match = re.search(r"<footer\b.*?</footer>", self.html, re.DOTALL)
        self.assertIsNotNone(footer_match, "no <footer> element")
        self.assertIn("images/brand/pecan-house-logo.png", footer_match.group(0),
                      "updated PNG logo should appear inside the footer")

    def test_footer_logo_max_width(self):
        css = STYLES.read_text(encoding="utf-8")
        self.assertRegex(css, r"\.footer-logo\s*\{[^}]*max-width:\s*280px",
                         "footer logo should be capped at 280px wide per instructions")

    def test_updated_logo_is_png(self):
        self.assertEqual(BRAND_LOGO.suffix, ".png")


class TestAboutDesignContext(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX.read_text(encoding="utf-8")
        cls.doc = parse(cls.html)

    def test_preview_section_removed(self):
        ids = {e["attrs"].get("id") for e in self.doc.elements}
        self.assertNotIn("preview", ids)
        self.assertNotIn(">Preview<", self.html)

    def test_rendering_context_is_merged_into_about(self):
        about_match = re.search(r'<section class="section" id="about">.*?</section>', self.html, re.DOTALL)
        self.assertIsNotNone(about_match, "About section missing")
        about_html = about_match.group(0)
        self.assertIn("The renovation direction pairs restored historic detail", about_html)
        self.assertIn("Renderings and design mockups will be replaced", about_html)

    def test_preview_css_removed(self):
        css = STYLES.read_text(encoding="utf-8")
        self.assertNotIn("design-preview", css)
        self.assertNotIn("preview-grid", css)


# ───────────────────────── Asset integrity ─────────────────────────── #

class TestAssetIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX.read_text(encoding="utf-8")
        cls.css = STYLES.read_text(encoding="utf-8")
        cls.doc = parse(cls.html)

    def _assert_local_path_exists(self, path: str, source: str):
        if (
            not path
            or path.startswith("#")
            or path.startswith("[")
            or path.startswith("http")
            or path.startswith("mailto:")
            or path.startswith("data:")
        ):
            return
        clean = path.split("#", 1)[0].split("?", 1)[0]
        if clean.endswith((".svg", ".png", ".jpg", ".jpeg", ".webp", ".css", ".js")):
            self.assertTrue((ROOT / clean).is_file(), f"{source} references missing asset: {path}")

    def test_html_asset_references_exist(self):
        for element in self.doc.elements:
            attrs = element["attrs"]
            for attr in ("src", "href", "content"):
                self._assert_local_path_exists(attrs.get(attr, ""), f"<{element['tag']}> {attr}")

    def test_css_url_assets_exist(self):
        for raw_url in re.findall(r"url\(([^)]+)\)", self.css):
            path = raw_url.strip().strip("\"'")
            self._assert_local_path_exists(path, "styles.css url()")


# ─────────────────────────── Brand & CSS ────────────────────────────── #

class TestBrandCss(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = STYLES.read_text(encoding="utf-8")

    def test_braces_balanced(self):
        self.assertEqual(self.css.count("{"), self.css.count("}"))

    def test_brand_palette_defined(self):
        for var in ("--color-bg", "--color-text", "--color-accent",
                    "--color-accent-dark", "--color-muted"):
            self.assertRegex(self.css, rf"{re.escape(var)}\s*:",
                             f"brand variable {var} not defined in :root")

    def test_palette_uses_approved_hexes(self):
        # Updated logo/mood board colors.
        for hex_value in ("#F3EFE6", "#2D2D2D", "#7C8B6F", "#4D5A3D", "#A69786"):
            self.assertIn(hex_value, self.css,
                          f"brand color {hex_value} missing from styles.css")

    def test_no_legacy_colors(self):
        # Old palette shouldn't linger.
        for legacy in ("#faf7f2", "#1f2421", "#2d3a2e", "#8a6a3b"):
            self.assertNotIn(legacy, self.css,
                             f"legacy color {legacy} still present — replace with brand vars")
        self.assertNotIn("#e1b97a", self.css,
                         "legacy accent #e1b97a still present")
        for prior in ("#F5F1E8", "#2B2419", "#8A8B5C", "#5C5D3A", "#A89F8C"):
            self.assertNotIn(prior, self.css,
                             f"prior logo palette {prior} still present")

    def test_buttons_are_rectangular(self):
        # Pills (border-radius: 999px) should be gone.
        self.assertNotRegex(self.css, r"\.btn[^{]*\{[^}]*border-radius:\s*999px",
                            "buttons should be rectangular per instructions, not pills")
        # Buttons should reference the small radius token.
        self.assertRegex(self.css, r"\.btn\s*\{[^}]*border-radius:\s*var\(--radius-sm\)",
                         "buttons should use --radius-sm")

    def test_buttons_use_brand_colors(self):
        self.assertRegex(self.css,
                         r"\.btn-primary\s*\{[^}]*background:\s*var\(--color-accent\)",
                         "btn-primary background should be --color-accent")
        self.assertRegex(self.css,
                         r"\.btn-primary[^{]*\{[^}]*color:\s*var\(--color-bg\)",
                         "btn-primary text should be --color-bg")
        self.assertRegex(self.css,
                         r"\.btn-primary:hover\s*\{[^}]*var\(--color-accent-dark\)",
                         "btn-primary hover should use --color-accent-dark")

    def test_serif_font_token_uses_brand(self):
        self.assertRegex(self.css, r"--serif:\s*[^;]*Cormorant Garamond",
                         "--serif token should reference Cormorant Garamond")
        self.assertRegex(self.css, r"--body:\s*[^;]*Lora",
                         "--body token should reference Lora")

    def test_section_labels_have_wide_tracking(self):
        # Section labels in small caps with wide tracking.
        match = re.search(r"\.eyebrow\s*\{[^}]*\}", self.css, re.DOTALL)
        self.assertIsNotNone(match, ".eyebrow rule missing")
        block = match.group(0)
        self.assertIn("uppercase", block, ".eyebrow should be uppercase")
        # 0.16em+ counts as "wide tracking".
        ls_match = re.search(r"letter-spacing:\s*([\d.]+)em", block)
        self.assertIsNotNone(ls_match, ".eyebrow needs letter-spacing in em")
        self.assertGreaterEqual(float(ls_match.group(1)), 0.16,
                                ".eyebrow letter-spacing should be ≥0.16em")

    def test_responsive_breakpoints_present(self):
        self.assertGreaterEqual(len(re.findall(r"@media[^{]*max-width", self.css)), 3)

    def test_no_lingering_todos(self):
        for marker in ("TODO", "FIXME", "XXX"):
            self.assertNotIn(marker, self.css)


# ─────────────────────────── JS structure ───────────────────────────── #

class TestScript(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.js = SCRIPT.read_text(encoding="utf-8")

    def test_braces_balanced(self):
        self.assertEqual(self.js.count("{"), self.js.count("}"))

    def test_parens_balanced(self):
        self.assertEqual(self.js.count("("), self.js.count(")"))

    def test_iife_wrap(self):
        self.assertRegex(self.js, r"\(\s*\(\)\s*=>\s*\{")

    def test_targets_nav_toggle(self):
        self.assertIn(".nav-toggle", self.js)
        self.assertIn("primary-nav", self.js)

    def test_toggles_is_open_class(self):
        self.assertIn("is-open", self.js)

    def test_updates_aria_expanded(self):
        self.assertIn("aria-expanded", self.js)

    def test_populates_year(self):
        self.assertIn('getElementById("year")', self.js)
        self.assertIn("getFullYear", self.js)



# ──────────────────────── Cloudflare _headers ───────────────────────── #

class TestHeaders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = HEADERS.read_text(encoding="utf-8")

    def test_security_headers_present(self):
        for header in (
            "X-Content-Type-Options: nosniff",
            "X-Frame-Options: DENY",
            "Referrer-Policy:",
            "Permissions-Policy:",
        ):
            self.assertIn(header, self.text)

    def test_caches_static_assets(self):
        self.assertRegex(self.text, r"/images/\*[^/]*?Cache-Control:\s*public")
        self.assertIn("immutable", self.text)


# ─────────────────────── Content accuracy ───────────────────────────── #

class TestContentAccuracy(unittest.TestCase):
    """Step 7 of instructions.md: privacy + factual accuracy of public copy."""

    @classmethod
    def setUpClass(cls):
        cls.html = INDEX.read_text(encoding="utf-8")
        cls.doc = parse(cls.html)
        cls.text = "".join(cls.doc.text_parts)

    def test_no_street_address_in_public_html(self):
        if not PRIVATE_STREET_ADDRESS:
            self.skipTest("PRIVATE_STREET_ADDRESS is not set")
        self.assertNotIn(PRIVATE_STREET_ADDRESS, self.html,
                         "Private street address "
                         "must not appear anywhere in index.html")

    def test_only_approved_location_phrasing(self):
        # Either "Texarkana, AR" or "Historic Texarkana, Arkansas" should appear.
        self.assertTrue(
            ("Texarkana, AR" in self.html) or ("Texarkana, Arkansas" in self.html),
            "expected approved location phrasing in HTML",
        )

    def test_correct_email_in_html(self):
        self.assertIn(PUBLIC_EMAIL, self.html,
                      f"contact email {PUBLIC_EMAIL} missing")

    def test_no_old_email_lingers(self):
        self.assertNotIn("hello@thepecanhouse.com", self.html,
                         "old placeholder email still present")

    def test_bedroom_count(self):
        self.assertIn("6 bedrooms", self.text,
                      "expected '6 bedrooms' in visible text")

    def test_bathroom_count(self):
        # Allow either "6 full bathrooms" or "Six baths" since both phrasings ship.
        self.assertTrue(
            re.search(r"\b6 full bathrooms\b", self.text) is not None
            or "Six baths" in self.text,
            "expected '6 full bathrooms' or 'Six baths' in visible text",
        )

    def test_two_kitchens(self):
        self.assertTrue(
            re.search(r"\b2 (full )?kitchens?\b", self.text) is not None
            or "Two kitchens" in self.text,
            "expected mention of 2 kitchens",
        )

    def test_sleeps_sixteen(self):
        self.assertTrue(
            "Sleeps up to 16" in self.html or "16" in self.text,
            "expected 'Sleeps up to 16'",
        )

    def test_pet_policy_complete(self):
        # Pet-free with the service-animal carveout per COPY.md and instructions.md.
        self.assertIn("pet-free", self.html.lower())
        self.assertIn("service animals", self.html.lower(),
                      "service animal carveout missing from pet policy")

    def test_removed_porch_copy(self):
        self.assertNotIn("wraparound", self.html.lower())
        self.assertNotIn("front porch", self.html.lower())


# ─────────────────────────── README sanity ──────────────────────────── #

class TestReadme(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = README.read_text(encoding="utf-8")

    def test_mentions_cloudflare_pages(self):
        self.assertIn("Cloudflare Pages", self.text)

    def test_documents_local_preview(self):
        self.assertIn("python3 -m http.server", self.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
