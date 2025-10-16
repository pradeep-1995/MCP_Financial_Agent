#!/bin/bash

# Telegram Webhook Setup Script for Financial AI Agent

set -e

TELEGRAM_TOKEN="8436070360:AAGIQ-j_EFEWEXlhoQyrAZ3kczu34Ik2vbg"
BASE_URL="https://api.telegram.org/bot${TELEGRAM_TOKEN}"

echo "==================================="
echo "Financial AI Agent - Telegram Setup"
echo "==================================="
echo ""

# Check if webhook URL is provided
if [ -z "$1" ]; then
    echo "Usage: ./setup_telegram.sh <your-backend-url>"
    echo ""
    echo "Examples:"
    echo "  ./setup_telegram.sh https://abc123.ngrok.io"
    echo "  ./setup_telegram.sh https://your-domain.com"
    echo ""
    echo "Note: URL must be accessible via HTTPS"
    exit 1
fi

BACKEND_URL="$1"
WEBHOOK_URL="${BACKEND_URL}/api/webhook"

echo "Backend URL: ${BACKEND_URL}"
echo "Webhook URL: ${WEBHOOK_URL}"
echo ""

# Check if URL is HTTPS
if [[ ! "$BACKEND_URL" =~ ^https:// ]]; then
    echo "⚠️  WARNING: URL should use HTTPS. HTTP webhooks may not work reliably."
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Setting webhook..."
RESPONSE=$(curl -s -X POST "${BASE_URL}/setWebhook" -d "url=${WEBHOOK_URL}")
echo "$RESPONSE" | python3 -m json.tool

echo ""
echo "Checking webhook status..."
curl -s "${BASE_URL}/getWebhookInfo" | python3 -m json.tool

echo ""
echo "==================================="
echo "Setup complete!"
echo ""
echo "Test your bot by sending a message:"
echo "  TSLA"
echo "or"
echo "  analyze AAPL"
echo "==================================="
