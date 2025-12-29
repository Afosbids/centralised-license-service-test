#!/bin/bash
set -e

BASE_URL="http://127.0.0.1:8000"

echo "=== Structured Logging Test ==="
echo ""

# Step 1: Generate API Key and check logs
echo "1. Performing an API call to trigger logs..."
API_KEY_RESPONSE=$(curl -s -i -X POST "$BASE_URL/api-keys/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Logging Test Key"}')

# Extract Request ID from headers
REQUEST_ID=$(echo "$API_KEY_RESPONSE" | grep -i "X-Request-ID" | awk '{print $2}' | tr -d '\r')

echo "Request ID returned in header: $REQUEST_ID"
echo ""

if [ -n "$REQUEST_ID" ]; then
    echo "✅ Success: Request ID found in response headers."
else
    echo "❌ Error: Request ID not found in response headers."
    exit 1
fi

# Step 2: Inform user about checking console output
echo "The backend console should now show JSON logs for this request."
echo "Look for a log entry containing: \"request_id\": \"$REQUEST_ID\""
echo ""

echo "=== Logging Test Complete ==="
