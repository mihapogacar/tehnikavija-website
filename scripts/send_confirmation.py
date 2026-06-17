#!/usr/bin/env python3
"""
Tehnikavija – order confirmation email sender.

Two modes
---------
1. CLI (manual / testing):

    python scripts/send_confirmation.py \
        --name     "Ana Kovač" \
        --email    "ana.kovac@example.com" \
        --product  "Colombia Huila (Medium, 250g) — 11 €" \
        --quantity 3 \
        --message  "Coarse grind for French press please."

2. Webhook server (receives the Web3Forms webhook POST):

    python scripts/send_confirmation.py --serve [--port 5000]

    Configure the Web3Forms webhook URL to:
        http://YOUR_SERVER:5000/webhook

Environment variables (put in .env or export before running):
    SMTP_HOST   – SMTP server, e.g. smtp.gmail.com
    SMTP_PORT   – 465 (SSL) or 587 (STARTTLS), default 465
    SMTP_USER   – your Gmail address (miha.pog@gmail.com)
    SMTP_PASS   – Gmail App Password (16-char, no spaces)
    FROM_NAME   – sender display name, default "Tehnikavija"
"""

import argparse
import html
import os
import smtplib
import ssl
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# ── optional .env loading (python-dotenv) ────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass  # python-dotenv not installed; rely on exported env vars

# ── paths ────────────────────────────────────────────────────────────────────
TEMPLATE_PATH = Path(__file__).parent.parent / "email-confirmation-template.html"


# ── template filler ──────────────────────────────────────────────────────────
def fill_template(name: str, email: str, product: str,
                  quantity: str, message: str) -> str:
    """Replace {{PLACEHOLDERS}} in the HTML template with order data."""
    body = TEMPLATE_PATH.read_text(encoding="utf-8")
    fields = {
        "{{NAME}}":     html.escape(name),
        "{{EMAIL}}":    html.escape(email),
        "{{PRODUCT}}":  html.escape(product),
        "{{QUANTITY}}": html.escape(str(quantity)),
        "{{NOTES}}":    html.escape(message) if message.strip() else "—",
    }
    for placeholder, value in fields.items():
        body = body.replace(placeholder, value)
    return body


# ── SMTP sender ───────────────────────────────────────────────────────────────
def send_confirmation(to_email: str, html_body: str) -> None:
    """Send the filled HTML template to the customer via SMTP."""
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 465))
    smtp_user = os.environ["SMTP_USER"]
    smtp_pass = os.environ["SMTP_PASS"]
    from_name = os.environ.get("FROM_NAME", "Tehnikavija")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your Tehnikavija order – confirmed ☕"
    msg["From"]    = f"{from_name} <{smtp_user}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    context = ssl.create_default_context()

    if smtp_port == 587:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())
    else:  # 465 SSL
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())

    print(f"✓ Confirmation sent to {to_email}")


# ── CLI mode ──────────────────────────────────────────────────────────────────
def run_cli(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Send a Tehnikavija order confirmation email."
    )
    parser.add_argument("--name",     required=True,  help="Customer name")
    parser.add_argument("--email",    required=True,  help="Customer email")
    parser.add_argument("--product",  required=True,  help="Product selected")
    parser.add_argument("--quantity", required=True,  help="Quantity ordered")
    parser.add_argument("--message",  default="",     help="Optional order notes")
    args = parser.parse_args(argv)

    body = fill_template(args.name, args.email, args.product,
                         args.quantity, args.message)
    send_confirmation(args.email, body)


# ── Webhook server mode ───────────────────────────────────────────────────────
def run_server(port: int = 5000) -> None:
    try:
        from flask import Flask, jsonify, request
    except ImportError:
        sys.exit("Flask is required for server mode. Run: pip install flask")

    app = Flask(__name__)

    @app.route("/webhook", methods=["POST"])
    def webhook():
        # Web3Forms sends form data as JSON or form-encoded
        data = request.get_json(silent=True) or request.form

        name     = (data.get("name")     or "").strip()
        email    = (data.get("email")    or "").strip()
        product  = (data.get("product")  or "").strip()
        quantity = (data.get("quantity") or "").strip()
        message  = (data.get("message")  or "").strip()

        if not email:
            return jsonify({"error": "missing email"}), 400

        try:
            body = fill_template(name, email, product, quantity, message)
            send_confirmation(email, body)
            return jsonify({"status": "ok"}), 200
        except KeyError as exc:
            return jsonify({"error": f"missing env var: {exc}"}), 500
        except Exception as exc:  # noqa: BLE001
            return jsonify({"error": str(exc)}), 500

    print(f"Webhook server running on port {port}  →  POST /webhook")
    app.run(host="0.0.0.0", port=port)


# ── entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if "--serve" in sys.argv:
        port_arg = None
        if "--port" in sys.argv:
            idx = sys.argv.index("--port")
            port_arg = int(sys.argv[idx + 1])
        run_server(port=port_arg or 5000)
    else:
        run_cli()
