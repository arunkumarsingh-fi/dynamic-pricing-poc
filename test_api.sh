#!/bin/bash

echo "🧪 Testing Dynamic Pricing API Endpoints"
echo "========================================"
echo ""

# Test 1: Health Check (GET request)
echo "1️⃣ Testing Health Check (GET /health):"
curl -s -X GET http://localhost:5002/health | jq '.'
echo ""

# Test 2: Price Recommendation (POST request)
echo "2️⃣ Testing Price Recommendation (POST /recommend_price):"
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "Model": "iPhone 13 Pro",
    "Battery": 95,
    "Screen_Damage": 0,
    "Backglass_Damage": 0,
    "market": "poland"
  }' \
  http://localhost:5002/recommend_price | jq '.recommended_price_eur, .pricing_strategy'
echo ""

# Test 3: Multi-Market Optimization (POST request)
echo "3️⃣ Testing Multi-Market Optimization (POST /optimize_market_and_price):"
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "Model": "iPhone 13 Pro",
    "Battery": 95,
    "Screen_Damage": 0,
    "Backglass_Damage": 0
  }' \
  http://localhost:5002/optimize_market_and_price | jq '.best_option.market, .best_option.selling_price_eur'
echo ""

# Test 4: Price Analysis (POST request)
echo "4️⃣ Testing Price Analysis (POST /price_analysis):"
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "Model": "iPhone 13",
    "Battery": 90,
    "Screen_Damage": 0,
    "Backglass_Damage": 0
  }' \
  http://localhost:5002/price_analysis | jq '.estimated_market_value'
echo ""

# Test 5: Report Outcome - will fail with invalid ID (demonstration)
echo "5️⃣ Testing Report Outcome (POST /report_outcome) - Expected to fail:"
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "decision_id": "invalid_id",
    "actual_reward": 100,
    "sale_outcome": "Device Sold"
  }' \
  http://localhost:5002/report_outcome | jq '.'
echo ""

echo "✅ API Testing Complete!"
echo ""
echo "💡 Notes:"
echo "- Only /health supports GET requests"
echo "- All other endpoints require POST with JSON data"
echo "- Use the Streamlit UI at http://localhost:8502 for interactive testing"
