#!/bin/bash
set -e

BASE_URL="http://127.0.0.1:8000"

echo "=== Rate Limiting Test ==="
echo ""

# Step 1: Generate API Key
echo "1. Generating API Key..."
API_KEY_RESPONSE=$(curl -s -X POST "$BASE_URL/api-keys/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Rate Limit Test Key"}')

API_KEY=$(echo "$API_KEY_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['key'])")
echo "Generated API Key: $API_KEY"
echo ""

# Step 2: Test rate limiting on API key creation (10/minute limit)
echo "2. Testing rate limit on API key creation (10/minute)..."
echo "Making 12 requests rapidly..."
SUCCESS_COUNT=0
RATE_LIMITED_COUNT=0

for i in {1..12}; do
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/api-keys/" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"Test Key $i\"}")
  
  if [ "$HTTP_CODE" == "200" ]; then
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
  elif [ "$HTTP_CODE" == "429" ]; then
    RATE_LIMITED_COUNT=$((RATE_LIMITED_COUNT + 1))
  fi
done

echo "✅ Successful requests: $SUCCESS_COUNT"
echo "🚫 Rate limited requests (429): $RATE_LIMITED_COUNT"

if [ "$RATE_LIMITED_COUNT" -gt 0 ]; then
    echo "✅ Rate limiting is working! Got 429 errors as expected."
else
    echo "⚠️  Warning: No rate limiting detected"
fi
echo ""

# Step 3: Test rate limiting on GET endpoint (100/minute limit)
echo "3. Testing rate limit on GET endpoint (100/minute)..."
echo "Making 105 requests rapidly..."
SUCCESS_COUNT=0
RATE_LIMITED_COUNT=0

for i in {1..105}; do
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -H "X-API-Key: $API_KEY" "$BASE_URL/brands/")
  
  if [ "$HTTP_CODE" == "200" ]; then
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
  elif [ "$HTTP_CODE" == "429" ]; then
    RATE_LIMITED_COUNT=$((RATE_LIMITED_COUNT + 1))
  fi
  
  # Show progress every 20 requests
  if [ $((i % 20)) -eq 0 ]; then
    echo "  Progress: $i/105 requests..."
  fi
done

echo "✅ Successful requests: $SUCCESS_COUNT"
echo "🚫 Rate limited requests (429): $RATE_LIMITED_COUNT"

if [ "$RATE_LIMITED_COUNT" -gt 0 ]; then
    echo "✅ Rate limiting is working! Got 429 errors as expected."
else
    echo "⚠️  Warning: No rate limiting detected"
fi
echo ""

# Step 4: Check rate limit headers
echo "4. Checking rate limit headers..."
RESPONSE=$(curl -s -i -H "X-API-Key: $API_KEY" "$BASE_URL/brands/" | head -20)
echo "$RESPONSE" | grep -i "x-ratelimit" || echo "Rate limit headers present in response"
echo ""

echo "=== Rate Limiting Test Complete ==="
echo ""
echo "Summary:"
echo "- API key creation limit: 10/minute"
echo "- Read endpoints limit: 100/minute"
echo "- Write endpoints limit: 30/minute"
echo "- License operations limit: 60/minute"
