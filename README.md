# Tehnikavija Website

A responsive static landing page for the Tehnikavija coffee brand.

## Local Preview

Open `index.html` in a browser, or use a local server:

```bash
npx serve .
```

## Deployment (GitHub Pages)

1. Push this repo to GitHub.
2. Go to **Settings → Pages**.
3. Set source to **Deploy from a branch** → `main` / root (`/`).
4. Your site will be live at `https://<username>.github.io/<repo-name>/`.

If you have a custom domain (e.g., `tehnikavija.com`), add it in the Pages settings and create a `CNAME` file.

## Analytics (GoatCounter)

Privacy-friendly, cookie-free, GDPR-compliant, and **free** for personal/small sites.

### Setup

1. Sign up at [goatcounter.com](https://www.goatcounter.com/).
2. Choose a site code (e.g., `tehnikavija`).
3. In `index.html`, replace `YOURSITE` with your site code:
   ```html
   <script data-goatcounter="https://tehnikavija.goatcounter.com/count"
           async src="//gc.zgo.at/count.js"></script>
   ```
4. View your dashboard at `https://tehnikavija.goatcounter.com/`.

GoatCounter tracks page views, referrers (including QR code scans), browser/OS info — all without cookies.

## QR Code

Once your site is live, generate a QR code pointing to your URL using any generator (e.g., [qr-code-generator.com](https://www.qr-code-generator.com/)).

**Tip**: To track QR scans separately, use a URL with a UTM parameter:
```
https://<your-site>/?ref=qr
```
GoatCounter will show this as a separate referrer in your dashboard.

## Structure

```
index.html          Main page
css/style.css       Styles
assets/             Logo, favicon, images (add your own)
README.md           This file
```
