#!/bin/bash
set -e

BASE_URL="http://127.0.0.1:8000"

echo "=== API Key Authentication Test ==="
echo ""

# Step 1: Generate API Key
echo "1. Generating API Key..."
API_KEY_RESPONSE=$(curl -s -X POST "$BASE_URL/api-keys/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Key", "brand_id": null}')

echo "$API_KEY_RESPONSE" | python3 -m json.tool

# Extract the API key
API_KEY=$(echo "$API_KEY_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['key'])")
echo ""
echo "Generated API Key: $API_KEY"
echo ""

# Step 2: Test endpoint WITHOUT API key (should fail)
echo "2. Testing endpoint WITHOUT API key (should return 401)..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/brands/")
if [ "$HTTP_CODE" == "401" ]; then
    echo "✅ Correctly rejected request without API key (401)"
else
    echo "❌ Expected 401, got $HTTP_CODE"
    exit 1
fi
echo ""

# Step 3: Test endpoint WITH valid API key (should succeed)
echo "3. Testing endpoint WITH valid API key (should succeed)..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -H "X-API-Key: $API_KEY" "$BASE_URL/brands/")
if [ "$HTTP_CODE" == "200" ]; then
    echo "✅ Successfully authenticated with API key (200)"
else
    echo "❌ Expected 200, got $HTTP_CODE"
    exit 1
fi
echo ""

# Step 4: Create a brand with API key
echo "4. Creating brand with API key..."
curl -s -X POST "$BASE_URL/brands/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"name": "Authenticated Brand", "email": "auth@test.com"}' | python3 -m json.tool
echo ""

# Step 5: List API keys
echo "5. Listing API keys..."
curl -s -H "X-API-Key: $API_KEY" "$BASE_URL/api-keys/" | python3 -m json.tool
echo ""

# Step 6: Test with invalid API key (should fail)
echo "6. Testing with INVALID API key (should return 401)..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -H "X-API-Key: invalid_key_12345" "$BASE_URL/brands/")
if [ "$HTTP_CODE" == "401" ]; then
    echo "✅ Correctly rejected invalid API key (401)"
else
    echo "❌ Expected 401, got $HTTP_CODE"
    exit 1
fi
echo ""

echo "=== All Authentication Tests Passed! ==="
