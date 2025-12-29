#!/bin/bash
set -e

echo "=== HTTPS / SSL Configuration Test ==="
echo ""

# Step 1: Check HTTP to HTTPS Redirection
echo "1. Testing HTTP to HTTPS redirection..."
STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/)
if [ "$STATUS_CODE" == "301" ]; then
    echo "✅ Success: HTTP (port 80) redirects with 301 Status Code."
else
    echo "❌ Error: Expected 301 Status Code, got $STATUS_CODE."
    exit 1
fi

REDIRECT_URL=$(curl -s -I http://localhost/ | grep -i "location" | awk '{print $2}' | tr -d '\r')
echo "Redirect URL: $REDIRECT_URL"
if [[ "$REDIRECT_URL" == https://* ]]; then
    echo "✅ Success: Redirection points to HTTPS."
else
    echo "❌ Error: Redirection does not point to HTTPS."
    exit 1
fi
echo ""

# Step 2: Test HTTPS access (ignoring cert validation for self-signed)
echo "2. Testing HTTPS access (ignoring self-signed certificate)..."
STATUS_CODE=$(curl -s -k -o /dev/null -w "%{http_code}" https://localhost/)
if [ "$STATUS_CODE" == "200" ]; then
    echo "✅ Success: Frontend accessible via HTTPS."
else
    echo "❌ Error: Expected 200 Status Code for frontend, got $STATUS_CODE."
    exit 1
fi
echo ""

# Step 3: Test Backend API via HTTPS proxy
echo "3. Testing Backend API via HTTPS proxy (/api/)..."
STATUS_CODE=$(curl -s -k -o /dev/null -w "%{http_code}" https://localhost/api/)
if [ "$STATUS_CODE" == "200" ]; then
    echo "✅ Success: Backend API accessible via HTTPS proxy."
else
    echo "❌ Error: Expected 200 Status Code for API health check, got $STATUS_CODE."
    exit 1
fi
echo ""

# Step 4: Verify Security Headers (HSTS)
echo "4. Verifying Security Headers (HSTS)..."
HSTS_HEADER=$(curl -s -k -I https://localhost/ | grep -i "Strict-Transport-Security")
if [ -n "$HSTS_HEADER" ]; then
    echo "✅ Success: HSTS header is present."
    echo "Header: $HSTS_HEADER"
else
    echo "❌ Error: HSTS header is missing."
    exit 1
fi

echo ""
echo "=== HTTPS Test Complete ==="
