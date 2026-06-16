# Tehnikavija Website — Chat Context

Use this file to resume work in a new chat. Paste it in as your first message.

---

## Project

Static landing page + sales funnel for **Tehnikavija**, a small-batch specialty coffee roasting brand.
Owner contact: `miha.pog@gmail.com`

## Stack

- Plain HTML/CSS (no build step)
- Hosted on **GitHub Pages** (not yet deployed)
- Analytics: **GoatCounter** (not yet configured)
- Order form → email: **Web3Forms** (not yet configured)
- Tests: **Python + Playwright + pytest**

## File Structure

```
tehnikavija-website/
├── index.html               # Main landing page (sales funnel)
├── css/style.css            # All styles
├── assets/
│   └── tehnikavija.svg      # Brand logo (SVG, ~165×40mm, used inverted white on dark hero)
├── tests/
│   └── test_customer_journey.py   # Playwright E2E tests (18 tests, all passing)
├── pytest.ini
└── CHAT_CONTEXT.md          # This file
```

## Page Structure (index.html)

1. **Hero** — SVG logo (`filter: brightness(0) invert(1)` for white on dark bg), tagline, "Order Now" CTA button scrolling to `#order`
2. **Intro** — Short brand paragraph (placeholder text, needs owner's copy)
3. **Current Offering** — 3 product cards (placeholder coffees: Ethiopia Yirgacheffe light 12€, Colombia Huila medium 11€, Guatemala Antigua dark 10€)
4. **Order Form** (`#order`) — Name, email, product dropdown, quantity (1–20), optional notes → POST to `https://api.web3forms.com/submit`
5. **Footer** — `miha.pog@gmail.com`, Instagram/Facebook links (hrefs are `#` placeholders)

## Pending Owner Actions

| # | Action | Where |
|---|---|---|
| 1 | **Web3Forms**: sign up at web3forms.com with `miha.pog@gmail.com`, get Access Key, replace `YOUR_WEB3FORMS_ACCESS_KEY` in `index.html` | `index.html` hidden input |
| 2 | **GoatCounter**: sign up at goatcounter.com, choose site code (e.g. `tehnikavija`), replace `YOURSITE` in `index.html` analytics script | `index.html` `<head>` |
| 3 | **GitHub**: create repo, push, enable Pages (Settings → Pages → main / root) | GitHub |
| 4 | **QR code**: after site is live, generate at qr-code-generator.com pointing to `https://user.github.io/repo/?ref=qr` | — |
| 5 | **Content**: replace placeholder intro text, product names/prices/tasting notes, social hrefs | `index.html` |
| 6 | **Favicon**: add `assets/favicon.ico` | `assets/` |

## Test Suite

File: `tests/test_customer_journey.py`
Run with: `python -m pytest tests/test_customer_journey.py -v`

18 tests across 4 classes:
- `TestPageLoad` — title, logo, tagline, CTA button
- `TestProductCatalogue` — 3 cards, names/prices/badges
- `TestOrderFormValidation` — required fields, honeypot hidden, empty submit blocked
- `TestOrderPlacement` — simulates "Ana Kovač" filling and submitting the form; intercepts Web3Forms API call and verifies full payload
- `TestMobileResponsive` — viewport 375×812, no horizontal scroll, cards stack vertically, inputs usable

**Bug found & fixed during testing:** `novalidate` was on the `<form>` tag, allowing empty submissions through to Web3Forms. Removed.

## Design Tokens (css/style.css)

```css
--color-bg: #faf8f5
--color-text: #2c2420
--color-accent: #6b4226
--color-accent-light: #a0714f
--color-muted: #7a6b63
--color-border: #e8e0d8
--color-hero-bg-top: #2c2420
--color-hero-bg-bottom: #4a3328
--font-main: 'Georgia', serif
--radius: 8px
```

## Known Placeholder Values in index.html

```
YOUR_WEB3FORMS_ACCESS_KEY   → replace after Web3Forms signup
YOURSITE                    → replace after GoatCounter signup
href="#"                    → Instagram and Facebook URLs
Intro paragraph             → owner's brand story
Product cards               → owner's actual coffee varieties, prices, tasting notes
```
