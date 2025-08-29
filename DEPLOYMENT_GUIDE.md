# 🔄 Full Circle Exchange: Complete Deployment Guide

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Container Deployment](#container-deployment)
3. [Local Development](#local-development)
4. [Using the Application](#using-the-application)
5. [Troubleshooting](#troubleshooting)
6. [Advanced Configuration](#advanced-configuration)

## 🚀 Quick Start

### Fastest Path to Running
```bash
# 1. Clone repository
git clone <repository>
cd dynamic_pricing_poc

# 2. One-command deployment
./deploy.sh
```
**Access**: http://localhost:8502

## 🐳 Container Deployment

### Prerequisites
```bash
# Install Podman
brew install podman                    # macOS
sudo apt-get install podman           # Ubuntu/Debian
sudo dnf install podman               # Fedora/RHEL

# Install podman-compose
pip install podman-compose
```

### Deployment Commands
```bash
# Deploy application
./deploy.sh deploy

# Management commands
./deploy.sh stop      # Stop services
./deploy.sh restart   # Restart services  
./deploy.sh logs      # View logs
./deploy.sh status    # Check status
./deploy.sh clean     # Clean up
```

### Container Architecture
- **full-circle-ml**: ML API server (Port 5002)
- **full-circle-ui**: Streamlit UI (Port 8502)
- **Shared Volume**: `/data` for analytics and feedback storage

## 🔧 Local Development

### Setup
```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Generate demo data
python etl_worker/etl_task.py

# 3. Start ML API (Terminal 1)
python ml_model/price_recommendation_app.py

# 4. Start UI (Terminal 2)
streamlit run ui_app/ui.py --server.port=8502
```

### Development Workflow
1. Make code changes
2. Restart relevant service
3. Test functionality
4. Use `./deploy.sh restart` for container testing

## 📱 Using the Application

### Tab 1: 📱 Story of a Unit
**Purpose**: Follow a single iPhone through its complete lifecycle

1. **Device Profile**: Select model, condition, battery health
2. **Market Context**: Set inventory levels, market timing
3. **Strategic Actions**: 
   - Single Market Analysis: Target specific market
   - Multi-Market Optimization: Find best opportunity
4. **Business Decision**: Record actual buying/selling outcomes
5. **Feedback Loop**: Train the AI with real results

### Tab 2: 📈 Day of Business  
**Purpose**: Portfolio-wide business intelligence

- **Business Health KPIs**: Revenue, profit, units sold
- **Financial Trends**: Monthly performance tracking
- **Strategic Deep Dive**: Model and market performance
- **Condition Impact**: How device condition affects profit

### Tab 3: 🚀 Optimized Business
**Purpose**: AI performance and continuous improvement

- **Executive Summary**: AI vs baseline performance comparison
- **Cumulative Gains**: Visualize AI learning over time
- **Strategy Breakdown**: Performance by pricing strategy
- **Decision History**: Track individual AI decisions

## 🔧 Troubleshooting

### Common Issues

**Problem**: Can't access UI at localhost:8502
```bash
# Check if containers are running
./deploy.sh status

# View container logs
./deploy.sh logs

# Check for port conflicts
lsof -i :8502
```

**Problem**: ML API not responding
```bash
# Check ML container specifically
podman logs full-circle-ml

# Test API directly
curl http://localhost:5002/health
```

**Problem**: No analytics data showing
```bash
# Regenerate demo data
python etl_worker/etl_task.py

# Restart containers to pick up new data
./deploy.sh restart
```

### Port Configuration
- **UI Port**: 8502 (not 8501 to avoid conflicts)
- **API Port**: 5002
- **Alternative**: Modify `podman-compose.yml` if needed

### Container Networking
Services communicate using container names:
- UI connects to ML API via `http://ml-backend:5002`
- Both containers share `/data` volume

## ⚙️ Advanced Configuration

### Environment Variables
```yaml
# In podman-compose.yml
environment:
  - ML_API_URL=http://ml-backend:5002
  - STREAMLIT_SERVER_PORT=8502
  - PYTHONUNBUFFERED=1
```

### Volume Mounting
```yaml
# Shared data volume
volumes:
  - ./data:/app/data
```

### Custom Configuration
1. **Different Ports**: Edit `podman-compose.yml` port mappings
2. **External Data**: Mount different data directory
3. **Production Mode**: Set environment variables for production URLs

### Performance Tuning
- **Memory**: Each container uses ~200MB base + data
- **CPU**: Single core sufficient for demo, multi-core for production
- **Storage**: ~50MB for application + variable for data

## 🚀 Production Deployment

### Security Considerations
1. **Network**: Use internal networks for container communication
2. **Data**: Secure data volume mounting
3. **API**: Consider authentication for ML API in production

### Scaling
1. **Load Balancing**: Multiple UI containers behind load balancer
2. **API Scaling**: Multiple ML API containers for high throughput
3. **Data**: Consider database backend for production data

### Monitoring
```bash
# Health checks
curl http://localhost:5002/health
curl http://localhost:8502/_stcore/health

# Performance monitoring
./deploy.sh logs | grep -E "(ERROR|WARNING)"
```

---

## 📞 Support

**Deployment Issues**: Check this guide's troubleshooting section
**Application Usage**: See README.md for business guidance  
**Development**: Use local development mode for code changes

**Quick Help**:
```bash
./deploy.sh          # Deploy application
./deploy.sh logs     # Check what's happening
./deploy.sh status   # See if containers are running
```
