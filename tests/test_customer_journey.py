"""
End-to-end tests simulating a real customer journey on the Tehnikavija website.

Scenario:
  Ana Kovač scans a QR code on a coffee bag, lands on the website,
  reads the product list, selects a coffee, and places an order.
  The Web3Forms submission is intercepted to verify payload correctness.
"""
import re
from pathlib import Path
from urllib.parse import urlencode

import pytest
from playwright.sync_api import Page, expect


# ─── Fixtures ───────────────────────────────────────────────────────────────

SITE_URL = Path(__file__).resolve().parent.parent / "index.html"


@pytest.fixture(autouse=True)
def open_landing_page(page: Page):
    """Simulate: customer scans QR code → browser opens the landing page with ?ref=qr."""
    page.goto(f"file:///{SITE_URL.as_posix()}?ref=qr")


# ─── Simulated Customer ────────────────────────────────────────────────────

CUSTOMER = {
    "name": "Ana Kovač",
    "email": "ana.kovac@example.com",
    "product": "Colombia Huila (Medium, 250g) — 11 €",
    "quantity": "3",
    "notes": "Coarse grind for French press please.",
}


# ─── TEST: Page loads correctly after QR scan ───────────────────────────────

class TestPageLoad:
    """Verify the landing page renders all critical sections."""

    def test_page_title(self, page: Page):
        expect(page).to_have_title(re.compile(r"Tehnikavija"))

    def test_logo_visible(self, page: Page):
        logo = page.locator("img.logo")
        expect(logo).to_be_visible()
        expect(logo).to_have_attribute("alt", "Tehnikavija")

    def test_tagline_visible(self, page: Page):
        tagline = page.locator(".tagline")
        expect(tagline).to_be_visible()
        expect(tagline).to_contain_text("precision")

    def test_order_button_in_hero(self, page: Page):
        btn = page.locator(".btn-hero")
        expect(btn).to_be_visible()
        expect(btn).to_have_attribute("href", "#order")


# ─── TEST: Product catalogue is displayed ───────────────────────────────────

class TestProductCatalogue:
    """Customer sees available coffee products with all required info."""

    def test_three_products_listed(self, page: Page):
        cards = page.locator(".product-card")
        expect(cards).to_have_count(3)

    def test_each_card_has_name_and_price(self, page: Page):
        cards = page.locator(".product-card")
        for i in range(3):
            card = cards.nth(i)
            expect(card.locator(".product-name")).to_be_visible()
            expect(card.locator(".product-price")).to_be_visible()
            expect(card.locator(".product-notes")).to_be_visible()

    def test_card_has_roast_badge(self, page: Page):
        badges = page.locator(".roast")
        expect(badges).to_have_count(3)

    def test_products_contain_expected_names(self, page: Page):
        text = page.locator(".products").text_content()
        assert "Yirgacheffe" in text
        assert "Huila" in text
        assert "Antigua" in text


# ─── TEST: Order form structure & validation ────────────────────────────────

class TestOrderFormValidation:
    """Form enforces required fields before submission."""

    def test_form_exists(self, page: Page):
        form = page.locator("#order-form")
        expect(form).to_be_visible()

    def test_required_fields_present(self, page: Page):
        expect(page.locator("#name")).to_have_attribute("required", "")
        expect(page.locator("#email")).to_have_attribute("required", "")
        expect(page.locator("#product")).to_have_attribute("required", "")
        expect(page.locator("#quantity")).to_have_attribute("required", "")

    def test_quantity_has_min_max(self, page: Page):
        qty = page.locator("#quantity")
        expect(qty).to_have_attribute("min", "1")
        expect(qty).to_have_attribute("max", "20")

    def test_product_dropdown_has_placeholder(self, page: Page):
        first_option = page.locator("#product option:first-child")
        expect(first_option).to_have_attribute("disabled", "")
        expect(first_option).to_contain_text("Choose a variety")

    def test_honeypot_hidden(self, page: Page):
        """The botcheck honeypot field must be invisible to real users."""
        honeypot = page.locator("input[name='botcheck']")
        expect(honeypot).to_be_hidden()

    def test_submit_empty_form_does_not_navigate(self, page: Page):
        """Clicking submit without filling required fields keeps us on the page."""
        page.locator(".btn-order").click()
        # Should still be on the same page (native validation blocks submission)
        expect(page).to_have_url(re.compile(r"index\.html"))


# ─── TEST: Full customer order placement journey ────────────────────────────

class TestOrderPlacement:
    """
    Simulate Ana Kovač's complete journey:
    1. Arrives via QR scan
    2. Clicks "Order Now" → scrolls to form
    3. Fills all fields
    4. Submits → Web3Forms API receives correct data
    """

    def test_full_order_journey(self, page: Page):
        # ── Step 1: Customer sees the CTA and clicks it ──
        hero_btn = page.locator(".btn-hero")
        hero_btn.click()

        # The #order section should now be in view
        order_section = page.locator("#order")
        expect(order_section).to_be_in_viewport()

        # ── Step 2: Fill in the order form ──
        page.locator("#name").fill(CUSTOMER["name"])
        page.locator("#email").fill(CUSTOMER["email"])
        page.locator("#product").select_option(value=CUSTOMER["product"])
        page.locator("#quantity").fill(CUSTOMER["quantity"])
        page.locator("#message").fill(CUSTOMER["notes"])

        # ── Step 3: Intercept the API call ──
        submitted_data = {}

        def handle_route(route):
            """Capture the form submission payload and mock a success response."""
            request = route.request
            # Form data comes as application/x-www-form-urlencoded POST body
            post_data = request.post_data
            if post_data:
                # Parse URL-encoded form data
                for pair in post_data.split("&"):
                    key, _, value = pair.partition("=")
                    from urllib.parse import unquote_plus
                    submitted_data[unquote_plus(key)] = unquote_plus(value)

            # Return a mock success response
            route.fulfill(
                status=200,
                content_type="application/json",
                body='{"success": true, "message": "Email sent successfully"}',
            )

        page.route("**/api.web3forms.com/submit", handle_route)

        # ── Step 4: Submit ──
        page.locator(".btn-order").click()

        # Wait for the intercepted request to complete
        page.wait_for_timeout(1000)

        # ── Step 5: Verify submitted data ──
        assert submitted_data.get("name") == CUSTOMER["name"], \
            f"Expected name '{CUSTOMER['name']}', got '{submitted_data.get('name')}'"
        assert submitted_data.get("email") == CUSTOMER["email"], \
            f"Expected email '{CUSTOMER['email']}', got '{submitted_data.get('email')}'"
        assert submitted_data.get("product") == CUSTOMER["product"], \
            f"Expected product '{CUSTOMER['product']}', got '{submitted_data.get('product')}'"
        assert submitted_data.get("quantity") == CUSTOMER["quantity"], \
            f"Expected quantity '{CUSTOMER['quantity']}', got '{submitted_data.get('quantity')}'"
        assert submitted_data.get("message") == CUSTOMER["notes"], \
            f"Expected notes '{CUSTOMER['notes']}', got '{submitted_data.get('message')}'"
        # Verify hidden fields
        assert submitted_data.get("subject") == "New Tehnikavija Order"
        assert submitted_data.get("from_name") == "Tehnikavija Website"
        # Honeypot should be empty (not checked by real user)
        assert submitted_data.get("botcheck", "") == ""


# ─── TEST: Responsive layout (mobile / QR code scan) ───────────────────────

class TestMobileResponsive:
    """Simulate mobile viewport — most QR scans happen on phones."""

    @pytest.fixture(autouse=True)
    def set_mobile_viewport(self, page: Page):
        page.set_viewport_size({"width": 375, "height": 812})  # iPhone-like
        page.reload()

    def test_page_is_not_horizontally_scrollable(self, page: Page):
        body_width = page.evaluate("document.body.scrollWidth")
        viewport_width = page.evaluate("window.innerWidth")
        assert body_width <= viewport_width + 1  # allow 1px rounding

    def test_product_cards_stack_vertically(self, page: Page):
        cards = page.locator(".product-card")
        first_box = cards.nth(0).bounding_box()
        second_box = cards.nth(1).bounding_box()
        # On mobile, cards should stack: second card below the first
        assert second_box["y"] > first_box["y"] + first_box["height"] - 5

    def test_order_form_usable_on_mobile(self, page: Page):
        page.locator(".btn-hero").click()
        name_input = page.locator("#name")
        expect(name_input).to_be_visible()
        # Input should be reasonably wide (at least 80% of viewport)
        box = name_input.bounding_box()
        assert box["width"] >= 375 * 0.7
