#!/bin/bash

# 🎭 AI Pricing System Demo Setup Script
# Run this before your demo to ensure everything works perfectly

echo "🚀 Setting up AI Pricing System Demo..."
echo "======================================"

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: Please run this script from the dynamic_pricing_poc directory"
    exit 1
fi

echo "📋 Step 1: Checking Podman containers..."
BACKEND_STATUS=$(podman ps --format "{{.Names}}" | grep pricing-backend || echo "not_running")
FRONTEND_STATUS=$(podman ps --format "{{.Names}}" | grep pricing-frontend || echo "not_running")

if [ "$BACKEND_STATUS" = "not_running" ] || [ "$FRONTEND_STATUS" = "not_running" ]; then
    echo "🔄 Starting containers..."
    if [ "$BACKEND_STATUS" = "not_running" ]; then
        podman run -d --name pricing-backend \
            --network pricing-network \
            -p 5002:5002 \
            -v $(pwd)/data:/app/data:Z \
            localhost/pricing-backend:latest
    fi
    if [ "$FRONTEND_STATUS" = "not_running" ]; then
        podman run -d --name pricing-frontend \
            --network pricing-network \
            -p 8501:8501 \
            -e ML_API_URL=http://pricing-backend:5002 \
            -v $(pwd)/data:/app/data:Z \
            localhost/frontend:latest
    fi
    echo "⏳ Waiting for services to start..."
    sleep 10
else
    echo "✅ Containers are running"
fi

echo ""
echo "🔍 Step 2: Testing API connectivity..."

# Test backend API
API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5002/health)
if [ "$API_RESPONSE" = "200" ]; then
    echo "✅ Backend API is responding"
else
    echo "❌ Backend API not responding (HTTP $API_RESPONSE)"
    echo "   Checking backend logs..."
    podman logs pricing-backend --tail 10
fi

echo ""
echo "🧪 Step 3: Testing sample pricing request..."

# Test a sample pricing request
SAMPLE_RESPONSE=$(curl -s -X POST http://localhost:5002/recommend_price \
  -H "Content-Type: application/json" \
  -d '{
    "Model": "iPhone 13",
    "Battery": 90,
    "inventory_level": "decent",
    "Backglass_Damage": 0,
    "Screen_Damage": 0,
    "new_model_imminent": false,
    "market": "romania",
    "model": "LinTS"
  }' | jq -r '.recommended_price_eur // "error"')

if [ "$SAMPLE_RESPONSE" != "error" ] && [ "$SAMPLE_RESPONSE" != "" ]; then
    echo "✅ Sample pricing request successful (€$SAMPLE_RESPONSE)"
else
    echo "❌ Sample pricing request failed"
    echo "   Raw response: $SAMPLE_RESPONSE"
fi

echo ""
echo "🌐 Step 4: Testing multi-market optimization..."

# Test multi-market request
MULTIMARKET_RESPONSE=$(curl -s -X POST http://localhost:5002/optimize_market_and_price \
  -H "Content-Type: application/json" \
  -d '{
    "Model": "iPhone 13",
    "Battery": 90,
    "inventory_level": "decent", 
    "Backglass_Damage": 0,
    "Screen_Damage": 0,
    "new_model_imminent": false,
    "model": "LinTS"
  }' | jq -r '.best_option.market // "error"')

if [ "$MULTIMARKET_RESPONSE" != "error" ] && [ "$MULTIMARKET_RESPONSE" != "" ]; then
    echo "✅ Multi-market optimization working (Best: $MULTIMARKET_RESPONSE)"
else
    echo "❌ Multi-market optimization failed"
fi

echo ""
echo "💾 Step 5: Checking analytics data..."

if [ -f "data/analytics_data.csv" ]; then
    RECORD_COUNT=$(wc -l < data/analytics_data.csv)
    echo "✅ Analytics data ready ($RECORD_COUNT records)"
else
    echo "⚠️  Analytics data not found - running ETL..."
    python etl_worker/etl_task.py
    if [ $? -eq 0 ]; then
        echo "✅ ETL completed successfully"
    else
        echo "❌ ETL failed"
    fi
fi

echo ""
echo "🎭 Demo Readiness Check Complete!"
echo "================================="

# Final status summary
echo ""
echo "📊 System Status:"
echo "  Backend API:     $([ "$API_RESPONSE" = "200" ] && echo "✅ Ready" || echo "❌ Issues")"
echo "  Pricing Engine:  $([ "$SAMPLE_RESPONSE" != "error" ] && echo "✅ Ready" || echo "❌ Issues")"
echo "  Multi-Market:    $([ "$MULTIMARKET_RESPONSE" != "error" ] && echo "✅ Ready" || echo "❌ Issues")"
echo "  Analytics Data:  $([ -f "data/analytics_data.csv" ] && echo "✅ Ready" || echo "❌ Missing")"

echo ""
echo "🎪 Demo URLs:"
echo "  Frontend UI: http://localhost:8501"
echo "  Backend API: http://localhost:5002"

echo ""
echo "📝 Quick Demo Test Scenario:"
echo "  1. Go to http://localhost:8501"
echo "  2. Set: iPhone 14 Pro, 85% battery, back glass damaged"
echo "  3. Try single market (Romania) first"
echo "  4. Then try multi-market optimization"
echo "  5. Toggle 'Compare All AI Models' for wow factor"

# Check if browser can be opened automatically
if command -v open >/dev/null 2>&1; then
    echo ""
    read -p "🌐 Open browser automatically? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open http://localhost:8501
        echo "🎉 Browser opened! You're ready to demo!"
    fi
fi

echo ""
echo "🚀 Good luck with your demo!"
echo "   Tip: Run 'cat DEMO_GUIDE.md' for the complete demo script"
