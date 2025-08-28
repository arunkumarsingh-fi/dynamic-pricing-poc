# 🎭 Demo Cheat Sheet - Quick Reference

## 🚀 **Before You Start**
```bash
# Run this to verify everything works:
./demo_setup.sh

# Open the UI:
open http://localhost:8501
```

## 🎯 **Perfect Demo Device Setup**
```
📱 iPhone Model: iPhone 14 Pro
🔋 Battery: 85%
📺 Screen: Undamaged
🔙 Back Glass: Damaged
📦 Inventory: Low  
📅 New Release: No
```

## 📋 **The 5-Act Demo Flow**

### **Act 1: Problem (30 seconds)**
*"Multi-market iPhone refurbishing is complex - let AI optimize it"*

### **Act 2: Single Market (2 minutes)** 
1. Select **Romania** → **"Generate Price"**
2. **Wow moment:** "€195 selling, €137 buying, €58 profit"
3. Toggle **"Compare All AI Models"** 
4. **Big reveal:** "Three different AI strategies!"
5. Set **Custom Price** €220 → "You control final decision"

### **Act 3: Multi-Market (2 minutes)**
1. **"Find Best Market & Price"**
2. **Dramatic reveal:** "Greece: €87 vs Romania: €65 = 34% more profit!"
3. Show **market comparison table**
4. Toggle **AI comparison** for multi-market

### **Act 4: Learning (1 minute)**
1. **"Device Sold"** → €210, 5 days
2. **"Report Outcome"** → "AI learns!"
3. **Key message:** "Every sale makes it smarter"

### **Act 5: Analytics (30 seconds)**
- **Tab 2:** Business metrics
- **Tab 3:** AI vs baseline performance

## 🎪 **Power Phrases**
- *"34% profit improvement through AI"*
- *"Three AI models, same data, different strategies"*
- *"Every feedback makes the next decision better"*
- *"You control it, AI optimizes it"*

## 🚨 **If Things Go Wrong**

### **API Error?**
```bash
podman restart pricing-backend
# Wait 30 seconds, try again
```

### **UI Not Loading?**
```bash
podman restart pricing-frontend
# Wait 30 seconds, refresh browser
```

### **No Data in Analytics?**
```bash
python etl_worker/etl_task.py
# Refresh Tab 2
```

## 💡 **Demo Killer Features**
1. **Multi-market bar chart** (most visual)
2. **AI model comparison tables** (most impressive) 
3. **Manual override + AI intelligence** (most practical)
4. **Learning feedback loop** (most innovative)

## 🎯 **Audience-Specific Pivots**

### **For Executives:**
Focus on: Profit uplift, ROI, competitive advantage
Skip: Technical details

### **For Operations:**
Focus on: Ease of use, manual control, daily workflow
Skip: AI model details

### **For Technical:**
Focus on: Algorithms, learning mechanisms, architecture  
Skip: Business metrics

## ⚡ **Quick Recovery Lines**

**"How accurate is this?"**
→ *"Gets more accurate with YOUR data - learns from every sale you make"*

**"What if AI is wrong?"**  
→ *"You override it AND it learns from being wrong"*

**"Too complex?"**
→ *"One click gets you 5-market analysis vs hours of manual work"*

**"Does it really learn?"**
→ *"Every 'sold', 'reduced price', or 'returned' trains it better"*

## 🎪 **Demo Closer**
*"In 5 minutes you've seen AI that:*
- *Analyzes 5 markets instantly*
- *Shows 3 different AI strategies*  
- *Learns from every outcome*
- *Increased profit 34% automatically*

*Question: How much profit are you leaving on the table?"*

---

## 🔧 **Technical Backup Info**

**URLs:**
- Frontend: http://localhost:8501
- Backend: http://localhost:5002

**Container Commands:**
```bash
podman ps                          # Check status
podman logs pricing-backend        # Debug backend
podman logs pricing-frontend       # Debug frontend
podman restart pricing-backend     # Restart API
podman restart pricing-frontend    # Restart UI
```

**Test API:**
```bash
curl http://localhost:5002/health
```

---
**🎭 Break a leg! This system will genuinely impress your audience.**
