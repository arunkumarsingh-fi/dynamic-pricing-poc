import pandas as pd
import numpy as np
from typing import Dict, Tuple
import json

class ProfitPredictor:
    """
    Automated profit/loss prediction system for iPhone pricing
    Replaces manual feedback with data-driven predictions
    """
    
    def __init__(self):
        self.cost_factors = {
            # Base cost factors (as % of selling price)
            'acquisition_cost': 0.75,  # Cost to acquire the device
            'refurbishment_cost': 0.05,  # Repair/cleaning costs
            'operational_cost': 0.08,   # Storage, staff, utilities
            'platform_fee': 0.03,      # E-commerce platform fees
            'shipping_cost': 0.02      # Delivery costs
        }
        
        self.market_factors = {
            # Market condition multipliers
            'high_demand_models': ['iphone 13', 'iphone 14', 'iphone 12'],
            'seasonal_multiplier': 1.0,  # Holiday season, back-to-school
            'competition_factor': 1.0    # Market competition level
        }
    
    def predict_sale_probability(self, device_info: Dict, price_tier: float) -> float:
        """
        Predict probability of sale based on device condition and pricing tier
        
        Args:
            device_info: Dict with device specifications and condition
            price_tier: Pricing multiplier (0.9, 1.0, 1.1)
            
        Returns:
            float: Sale probability between 0 and 1
        """
        # Base sale probability by pricing tier
        base_probabilities = {
            0.9: 0.85,   # Discount pricing - high probability
            1.0: 0.70,   # Standard pricing - moderate probability  
            1.1: 0.45    # Premium pricing - lower probability
        }
        
        base_prob = base_probabilities.get(price_tier, 0.70)
        
        # Device condition adjustments
        battery_health = device_info.get('Battery', 95) / 100
        screen_damage = device_info.get('Screen_Damage', 0)
        backglass_damage = device_info.get('Backglass_Damage', 0)
        
        # Condition score (0-1)
        condition_score = battery_health * (1 - screen_damage * 0.3) * (1 - backglass_damage * 0.2)
        
        # Storage preference (higher storage = higher demand)
        storage = device_info.get('Storage', 128)
        storage_multiplier = min(1.2, 0.8 + (storage / 256) * 0.4)
        
        # Model popularity
        model = device_info.get('Model', '').lower()
        popularity_multiplier = 1.0
        for popular_model in self.market_factors['high_demand_models']:
            if popular_model in model:
                popularity_multiplier = 1.15
                break
        
        # Inventory level impact
        inventory_level = device_info.get('inventory_level', 'decent')
        inventory_multiplier = {
            'low': 0.95,    # Less pressure to sell
            'decent': 1.0,  # Normal conditions
            'high': 1.1     # More pressure to sell
        }.get(inventory_level, 1.0)
        
        # Market shock impact (new releases, economic events)
        market_shock = device_info.get('market_shock', 0)
        shock_multiplier = 0.85 if market_shock else 1.0
        
        # Calculate final probability
        final_prob = (base_prob * 
                     condition_score * 
                     storage_multiplier * 
                     popularity_multiplier * 
                     inventory_multiplier * 
                     shock_multiplier)
        
        return min(0.95, max(0.05, final_prob))  # Clamp between 5-95%
    
    def calculate_expected_profit(self, device_info: Dict, price_tier: float, 
                                base_price: float) -> Dict:
        """
        Calculate expected profit/loss for a pricing decision
        
        Args:
            device_info: Device specifications and condition
            price_tier: Pricing multiplier (0.9, 1.0, 1.1)
            base_price: Base market price in LKR
            
        Returns:
            Dict with profit calculations and metrics
        """
        # Calculate selling price
        selling_price = base_price * price_tier
        
        # Predict sale probability
        sale_probability = self.predict_sale_probability(device_info, price_tier)
        
        # Calculate costs
        total_cost = 0
        cost_breakdown = {}
        
        for factor, percentage in self.cost_factors.items():
            cost = selling_price * percentage
            cost_breakdown[factor] = cost
            total_cost += cost
        
        # Gross profit per unit
        gross_profit = selling_price - total_cost
        
        # Expected profit considering sale probability
        expected_profit = sale_probability * gross_profit
        
        # Holding costs (if item doesn't sell)
        holding_cost_per_day = selling_price * 0.001  # 0.1% per day
        expected_holding_days = (1 - sale_probability) * 30  # Assume 30 days if no sale
        expected_holding_cost = expected_holding_days * holding_cost_per_day
        
        # Net expected profit
        net_expected_profit = expected_profit - expected_holding_cost
        
        # Profit margin
        profit_margin = (gross_profit / selling_price) * 100 if selling_price > 0 else 0
        
        return {
            'selling_price': round(selling_price, 2),
            'total_cost': round(total_cost, 2),
            'gross_profit': round(gross_profit, 2),
            'expected_profit': round(net_expected_profit, 2),
            'sale_probability': round(sale_probability, 4),
            'profit_margin': round(profit_margin, 2),
            'cost_breakdown': {k: round(v, 2) for k, v in cost_breakdown.items()},
            'expected_holding_cost': round(expected_holding_cost, 2),
            'recommendation': self._generate_recommendation(sale_probability, profit_margin)
        }
    
    def _generate_recommendation(self, sale_prob: float, profit_margin: float) -> str:
        """Generate business recommendation based on metrics"""
        if sale_prob > 0.8 and profit_margin > 15:
            return "🎯 EXCELLENT: High sale probability with good margins"
        elif sale_prob > 0.7 and profit_margin > 10:
            return "✅ GOOD: Balanced risk and reward"
        elif sale_prob > 0.6 and profit_margin > 5:
            return "⚠️ MODERATE: Acceptable but monitor closely"
        elif sale_prob < 0.4:
            return "❌ HIGH RISK: Low sale probability - consider discount"
        elif profit_margin < 5:
            return "💸 LOW MARGIN: Consider cost optimization"
        else:
            return "📊 REVIEW: Mixed signals - needs analysis"
    
    def compare_pricing_tiers(self, device_info: Dict, base_price: float) -> Dict:
        """
        Compare all pricing tiers for a device
        
        Args:
            device_info: Device specifications and condition
            base_price: Base market price in LKR
            
        Returns:
            Dict with comparison of all tiers
        """
        tiers = [0.9, 1.0, 1.1]
        comparison = {}
        
        for tier in tiers:
            tier_analysis = self.calculate_expected_profit(device_info, tier, base_price)
            tier_name = {0.9: "Discount", 1.0: "Standard", 1.1: "Premium"}[tier]
            comparison[f"tier_{tier}_{tier_name}"] = tier_analysis
        
        # Find optimal tier
        best_tier = max(comparison.items(), 
                       key=lambda x: x[1]['expected_profit'])
        
        return {
            'tier_comparison': comparison,
            'optimal_tier': best_tier[0],
            'optimal_expected_profit': best_tier[1]['expected_profit'],
            'recommendation_summary': f"Recommend {best_tier[0]} with expected profit of ₹{best_tier[1]['expected_profit']:.2f}"
        }

def create_enhanced_feedback_system():
    """
    Demo function showing how to integrate profit prediction with the bandit system
    """
    predictor = ProfitPredictor()
    
    # Example device
    device_example = {
        'Storage': 256,
        'RAM': 6, 
        'Battery': 90,
        'Screen_Damage': 0,
        'Backglass_Damage': 0,
        'inventory_level': 'decent',
        'market_shock': 0,
        'Model': 'iphone 13 pro'
    }
    
    base_price = 180000  # ₹180,000 LKR
    
    # Get tier comparison
    analysis = predictor.compare_pricing_tiers(device_example, base_price)
    
    print("🔍 PROFIT PREDICTION ANALYSIS")
    print("=" * 50)
    
    for tier_name, metrics in analysis['tier_comparison'].items():
        print(f"\n📊 {tier_name.upper()}")
        print(f"   Selling Price: ₹{metrics['selling_price']:,.2f}")
        print(f"   Sale Probability: {metrics['sale_probability']:.1%}")
        print(f"   Expected Profit: ₹{metrics['expected_profit']:,.2f}")
        print(f"   Profit Margin: {metrics['profit_margin']:.1f}%")
        print(f"   {metrics['recommendation']}")
    
    print(f"\n🏆 OPTIMAL STRATEGY")
    print(f"   {analysis['recommendation_summary']}")
    
    return analysis

if __name__ == "__main__":
    # Run demonstration
    create_enhanced_feedback_system()
