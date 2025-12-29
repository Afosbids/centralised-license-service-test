#!/bin/bash
set -e

BASE_URL="http://127.0.0.1:8000"

echo "1. Create Brand"
curl -s -X POST "$BASE_URL/brands/" -H "Content-Type: application/json" -d '{"name": "Acme Inc", "email": "admin@acme.com"}' | grep "id"

echo -e "\n2. Create Product"
curl -s -X POST "$BASE_URL/products/" -H "Content-Type: application/json" -d '{"name": "SuperTool", "brand_id": 1}' | grep "id"

echo -e "\n3. Create Customer"
curl -s -X POST "$BASE_URL/customers/" -H "Content-Type: application/json" -d '{"email": "alice@example.com"}' | grep "id"

echo -e "\n4. GET /customers/"
curl -s "$BASE_URL/customers/" | grep "alice@example.com"

echo -e "\n5. Issue License"
curl -s -X POST "$BASE_URL/licenses/" -H "Content-Type: application/json" -d '{"customer_id": 1, "product_id": 1, "key": "KEY-TEST", "max_seats": 2}' | grep "id"

echo -e "\n6. Activate License"
ACTIVATION_RES=$(curl -s -X POST "$BASE_URL/licenses/activate" -H "Content-Type: application/json" -d '{"license_key": "KEY-TEST", "machine_id": "MAC-1", "friendly_name": "Alice Mac"}')
echo $ACTIVATION_RES
ACTIVATION_ID=$(echo $ACTIVATION_RES | grep -o '"id":[0-9]*' | cut -d: -f2)

echo -e "\n7. Deactivate Machine (ID: $ACTIVATION_ID)"
curl -s -X DELETE "$BASE_URL/activations/$ACTIVATION_ID"

echo -e "\n8. Suspend License (ID: 1)"
curl -s -X PUT "$BASE_URL/licenses/1/suspend" | grep "is_active\":false"

echo -e "\n9. Resume License (ID: 1)"
curl -s -X PUT "$BASE_URL/licenses/1/resume" | grep "is_active\":true"

echo -e "\n\nSUCCESS"
