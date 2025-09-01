# 🧪 Setup Verification Guide

## 🎯 New User Complete Setup Test

This guide helps verify that a completely fresh setup works correctly.

### 📋 Prerequisites Check
```bash
# 1. Check Podman installation
podman --version

# 2. Check Python installation  
python3 --version
# Should show Python 3.8+ 

# 3. Check pip
pip3 --version

# 4. Install podman-compose if needed
pip install podman-compose
```

### 🚀 Fresh Deployment Test
```bash
# 1. Clone the repository
git clone <your-repository-url>
cd dynamic_pricing_poc

# 2. Deploy with one command
./deploy.sh

# Expected output should show:
# ✅ Podman found
# ✅ podman-compose found  
# 📈 Generating synthetic transaction data (10k records)...
# ✅ Transaction data generated
# 🔨 Building and starting containers...
# 🎉 Full Circle Exchange deployed successfully!
```

### ✅ Verification Steps

#### **1. Container Status Check**
```bash
./deploy.sh status
# Should show both containers running:
# - full-circle-ml  
# - full-circle-ui
```

#### **2. API Health Check**
```bash
curl http://localhost:5002/health
# Should return: {"status":"healthy","models_loaded":["LinTS","LinUCB","EpsilonGreedy"],...}
```

#### **3. UI Access Check**
```bash
curl -I http://localhost:8502
# Should return: HTTP/1.1 200 OK
```

#### **4. Full API Test**
```bash
./test_api.sh
# Should show all endpoints working with ✅ status
```

#### **5. UI Functionality Test**
Visit http://localhost:8502 and verify:

**Tab 1 - Price Recommendation:**
- ✅ Can select iPhone model
- ✅ Can set battery/damage conditions  
- ✅ "Generate Price" button works
- ✅ Shows pricing recommendations

**Tab 2 - Analytics Dashboard:**
- ✅ Shows business KPIs
- ✅ Displays charts and graphs
- ✅ Market analysis visible
- ✅ No "Connection error" messages

**Tab 3 - AI Feedback:**
- ✅ Shows AI performance metrics
- ✅ Feedback history loads
- ✅ Can send feedback to bandit
- ✅ Charts render properly

### 🔧 Common New User Issues

#### **Issue**: Python module not found
```bash
# Solution: Install missing dependencies
pip install pandas numpy scikit-learn flask streamlit
```

#### **Issue**: Port already in use
```bash
# Check what's using the ports
lsof -i :8502
lsof -i :5002

# Kill conflicting processes or modify ports in podman-compose.yml
```

#### **Issue**: Containers build but don't start
```bash
# Check detailed logs
podman logs full-circle-ml
podman logs full-circle-ui

# Look for specific error messages
```

#### **Issue**: UI loads but no data
```bash
# Check if data was generated
ls -la data/

# Should see:
# - analytics_data.csv (>1MB)
# - ai_feedback_history.json

# If missing, regenerate:
python3 data_simulator.py
./deploy.sh restart
```

### 📊 Expected Success Metrics

After successful deployment, you should see:

1. **Data Generation**: 10,000 transaction records
2. **Container Status**: Both containers "Up" 
3. **API Health**: All endpoints responding
4. **UI Loading**: No connection errors
5. **Analytics**: Charts and KPIs displaying

### 🔄 Complete Reset (If Things Go Wrong)

```bash
# Nuclear option - completely clean slate
./deploy.sh clean
rm -rf data/
git clean -fd
./deploy.sh deploy
```

### 📞 Support Checklist

If you're still having issues, run this diagnostic:

```bash
echo "=== DIAGNOSTIC REPORT ===" 
echo "Date: $(date)"
echo "OS: $(uname -a)"
echo ""
echo "Podman Version:"
podman --version
echo ""
echo "Container Status:"
podman ps -a
echo ""
echo "Network Status:"
podman network ls
echo ""
echo "Port Status:"
lsof -i :5002 :8502 | head -10
echo ""
echo "Data Files:"
ls -la data/ 2>/dev/null || echo "No data directory"
echo ""
echo "=== END DIAGNOSTIC ==="
```

This report will help identify the specific issue area.
