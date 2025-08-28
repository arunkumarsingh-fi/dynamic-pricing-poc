#!/usr/bin/env python3

def demo_profit_calculation():
    """
    Demonstrate automatic profit/loss prediction vs manual feedback
    """
    print("💰 AUTOMATED PROFIT PREDICTION SYSTEM")
    print("=" * 60)
    
    # Example device: iPhone 13 Pro (256GB, 90% battery, no damage)
    device = {
        'model': 'iPhone 13 Pro',
        'storage': 256,
        'battery_health': 90,
        'screen_damage': False,
        'backglass_damage': False,
        'inventory_level': 'decent'
    }
    
    base_price = 180000  # ₹180,000 LKR (~$525 USD)
    
    print(f"📱 Device: {device['model']} ({device['storage']}GB)")
    print(f"🔋 Battery Health: {device['battery_health']}%")
    print(f"💎 Condition: Excellent (no damage)")
    print(f"📦 Inventory: {device['inventory_level']}")
    print(f"💵 Base Price: ₹{base_price:,} LKR")
    print()
    
    # Pricing tier analysis
    tiers = {
        0.9: {'name': 'Discount', 'sale_prob': 0.85, 'margin': 8},
        1.0: {'name': 'Standard', 'sale_prob': 0.72, 'margin': 15},
        1.1: {'name': 'Premium', 'sale_prob': 0.52, 'margin': 22}
    }
    
    print("🎯 PRICING TIER ANALYSIS")
    print("-" * 60)
    print(f"{'Tier':<12} {'Price':<12} {'Sale Prob':<12} {'Exp. Profit':<15} {'Recommendation':<20}")
    print("-" * 60)
    
    best_profit = 0
    best_tier = None
    
    for multiplier, data in tiers.items():
        selling_price = base_price * multiplier
        costs = selling_price * 0.85  # 85% costs (acquisition, operations, etc.)
        gross_profit = selling_price - costs
        expected_profit = gross_profit * data['sale_prob']
        
        if expected_profit > best_profit:
            best_profit = expected_profit
            best_tier = data['name']
        
        # Generate recommendation
        if data['sale_prob'] > 0.8 and data['margin'] > 15:
            rec = "🎯 Excellent"
        elif data['sale_prob'] > 0.6 and data['margin'] > 10:
            rec = "✅ Good"
        else:
            rec = "⚠️ Risky"
        
        print(f"{data['name']:<12} ₹{selling_price:>9,.0f} {data['sale_prob']:>10.0%} ₹{expected_profit:>12,.0f} {rec:<20}")
    
    print("-" * 60)
    print(f"🏆 OPTIMAL STRATEGY: {best_tier} tier (₹{best_profit:,.0f} expected profit)")
    print()
    
    print("🔄 CURRENT vs ENHANCED FEEDBACK SYSTEM")
    print("-" * 60)
    print("❌ CURRENT APPROACH:")
    print("   • Manual profit/loss entry")
    print("   • Subjective and inconsistent")
    print("   • Delayed feedback (after sale)")
    print("   • No predictive capability")
    print()
    
    print("✅ ENHANCED APPROACH:")
    print("   • Automatic profit prediction")
    print("   • Data-driven and consistent")
    print("   • Instant feedback (at decision time)")
    print("   • Predictive sale probability")
    print("   • Cost breakdown analysis")
    print("   • Risk assessment")
    print()
    
    print("💡 IMPLEMENTATION BENEFITS:")
    print("   • Remove manual intervention")
    print("   • Faster learning cycles")
    print("   • Better business insights")
    print("   • Consistent reward signals")
    print("   • Automated optimization")

if __name__ == "__main__":
    demo_profit_calculation()
