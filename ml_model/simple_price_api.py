#!/usr/bin/env python3
"""
Simple Price Recommendation API for testing
This is a simplified version that doesn't use MAB to ensure basic functionality works
"""

from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import uuid
import os
from datetime import datetime

app = Flask(__name__)

# Currency conversion rates
CURRENCY_RATES = {
    'LKR_TO_EUR': 0.0031,  # 1 LKR = 0.0031 EUR
    'USD_TO_EUR': 0.92     # 1 USD = 0.92 EUR
}

class SimplePriceEngine:
    """Simple pricing engine for testing"""
    
    def __init__(self):
        self.tier_multipliers = [0.9, 1.0, 1.1]
        self.tier_names = {
            0.9: "Competitive",
            1.0: "Market Rate", 
            1.1: "Premium"
        }
    
    def convert_lkr_to_eur(self, lkr_price):
        """Convert LKR price to EUR"""
        return round(lkr_price * CURRENCY_RATES['LKR_TO_EUR'], 2)
    
    def get_model_base_value(self, model_name):
        """Get base value for specific iPhone models"""
        model_values = {
            'iPhone 11': 45000,
            'iPhone 11 Pro': 65000,
            'iPhone 11 Pro Max': 70000,
            'iPhone 12': 55000,
            'iPhone 12 Mini': 50000,
            'iPhone 12 Pro': 75000,
            'iPhone 12 Pro Max': 80000,
            'iPhone 13': 65000,
            'iPhone 13 Mini': 60000,
            'iPhone 13 Pro': 85000,
            'iPhone 13 Pro Max': 90000,
            'iPhone 14': 75000,
            'iPhone 14 Plus': 80000,
            'iPhone 14 Pro': 95000,
            'iPhone 14 Pro Max': 100000,
            'iPhone 15': 85000,
            'iPhone 15 Plus': 90000,
            'iPhone 15 Pro': 110000,
            'iPhone 15 Pro Max': 120000
        }
        return model_values.get(model_name, 50000)  # Default value
    
    def estimate_market_price(self, device_info):
        """Estimate market price based on device specifications and iPhone model"""
        model_name = device_info.get('Model', 'iPhone 12')
        storage = device_info.get('Storage', 128)
        ram = device_info.get('RAM', 4)
        battery_health = device_info.get('Battery', 95)
        camera = device_info.get('Camera', 12)
        
        # Get model-specific base value
        base_value = self.get_model_base_value(model_name)
        
        # Storage multipliers based on model tier
        if 'Pro' in model_name:
            storage_multiplier = 1.0 + (storage / 128 - 1) * 0.3  # Pro models: 30% premium for higher storage
        else:
            storage_multiplier = 1.0 + (storage / 128 - 1) * 0.2  # Regular models: 20% premium
        
        # RAM impact (more significant for newer models)
        ram_multiplier = 1.0 + (ram - 4) * 0.05
        
        # Camera impact (especially for Pro models with 48MP)
        camera_multiplier = 1.0
        if camera == 48:
            camera_multiplier = 1.15  # 15% premium for 48MP cameras
        
        # Battery health impact
        battery_multiplier = battery_health / 100
        
        # Damage penalties
        screen_damage = device_info.get('Screen_Damage', 0)
        backglass_damage = device_info.get('Backglass_Damage', 0)
        damage_penalty = (screen_damage + backglass_damage) * 0.15
        
        # Market factors
        inventory_level = device_info.get('inventory_level', 'decent')
        inventory_multiplier = {
            'low': 1.05,    # 5% premium for low inventory
            'decent': 1.0,  # No change
            'high': 0.95    # 5% discount for high inventory
        }.get(inventory_level, 1.0)
        
        # Calculate estimated price
        estimated_price = (base_value * 
                          storage_multiplier * 
                          ram_multiplier * 
                          camera_multiplier * 
                          battery_multiplier * 
                          inventory_multiplier * 
                          (1 - damage_penalty))
        
        return max(20000, estimated_price)
    
    def get_simple_recommendation(self, device_info):
        """Simple rule-based recommendation"""
        storage = device_info.get('Storage', 128)
        battery = device_info.get('Battery', 95)
        inventory = device_info.get('inventory_level', 'decent')
        damage_total = device_info.get('Screen_Damage', 0) + device_info.get('Backglass_Damage', 0)
        
        # Simple decision logic
        if damage_total > 0 or battery < 80:
            return 0.9  # Competitive pricing for damaged/old devices
        elif storage >= 512 and battery >= 95 and inventory == 'low':
            return 1.1  # Premium for high-end devices with low inventory
        else:
            return 1.0  # Market rate for most devices
    
    def calculate_all_prices(self, base_price_lkr, recommended_tier):
        """Calculate prices for all tiers"""
        base_price_eur = self.convert_lkr_to_eur(base_price_lkr)
        
        prices = {}
        for tier in self.tier_multipliers:
            tier_price_eur = round(base_price_eur * tier, 2)
            prices[tier] = {
                'price_eur': tier_price_eur,
                'price_lkr': round(base_price_lkr * tier, 0),
                'strategy': self.tier_names[tier],
                'recommended': (tier == recommended_tier)
            }
        
        return prices

# Initialize the pricing engine
price_engine = SimplePriceEngine()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Simple Price Recommendation API',
        'version': '1.0',
        'currency': 'EUR'
    })

@app.route('/recommend_price', methods=['POST'])
def recommend_price():
    """Main price recommendation endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Get simple recommendation
        recommended_tier = price_engine.get_simple_recommendation(data)
        
        # Estimate market price
        estimated_market_price_lkr = price_engine.estimate_market_price(data)
        
        # Calculate all pricing options
        all_prices = price_engine.calculate_all_prices(estimated_market_price_lkr, recommended_tier)
        
        # Get recommended option details
        recommended_option = all_prices[recommended_tier]
        
        # Determine market segment
        storage = data.get('Storage', 128)
        if storage >= 512:
            market_segment = 'premium'
        elif storage >= 256:
            market_segment = 'high_end'
        elif storage >= 128:
            market_segment = 'mid_range'
        else:
            market_segment = 'budget'
        
        # Calculate condition score
        battery = data.get('Battery', 95)
        screen_damage = data.get('Screen_Damage', 0)
        backglass_damage = data.get('Backglass_Damage', 0)
        condition_score = battery * 0.4 + (1 - screen_damage) * 30 + (1 - backglass_damage) * 30
        
        decision_id = str(uuid.uuid4())
        
        response = {
            'decision_id': decision_id,
            'recommended_tier': float(recommended_tier),
            'recommended_price_eur': recommended_option['price_eur'],
            'recommended_price_lkr': recommended_option['price_lkr'],
            'pricing_strategy': recommended_option['strategy'],
            'model_used': 'SimpleRuleBased',
            'market_segment': market_segment,
            'condition_score': round(condition_score, 1),
            'estimated_market_value': {
                'eur': price_engine.convert_lkr_to_eur(estimated_market_price_lkr),
                'lkr': round(estimated_market_price_lkr, 0)
            },
            'all_pricing_options': all_prices,
            'currency_info': {
                'primary_currency': 'EUR',
                'conversion_rate': f"1 LKR = {CURRENCY_RATES['LKR_TO_EUR']} EUR"
            },
            'input_data': data
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/price_analysis', methods=['POST'])
def price_analysis():
    """Price analysis endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Estimate market price
        estimated_market_price_lkr = price_engine.estimate_market_price(data)
        
        # Get pricing for all tiers
        all_prices = {}
        for tier in [0.9, 1.0, 1.1]:
            prices = price_engine.calculate_all_prices(estimated_market_price_lkr, tier)
            all_prices.update(prices)
        
        response = {
            'device_specs': data,
            'estimated_market_value': {
                'eur': price_engine.convert_lkr_to_eur(estimated_market_price_lkr),
                'lkr': round(estimated_market_price_lkr, 0)
            },
            'pricing_analysis': all_prices,
            'currency_info': {
                'primary_currency': 'EUR',
                'conversion_rate': f"1 LKR = {CURRENCY_RATES['LKR_TO_EUR']} EUR"
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/report_outcome', methods=['POST'])
def report_outcome():
    """Report outcome endpoint (for UI compatibility)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        decision_id = data.get('decision_id')
        reward = data.get('reward')
        
        if not decision_id:
            return jsonify({'error': 'Decision ID required'}), 400
        
        # For the simple API, we just acknowledge the feedback
        # In a real implementation, this would update the ML model
        response = {
            'status': 'success',
            'message': f'Feedback recorded for decision {decision_id}',
            'reward': reward,
            'note': 'Simple API - feedback logged but not used for model updates'
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Simple Price Recommendation API',
        'version': '1.0',
        'endpoints': [
            'GET /health - Health check',
            'POST /recommend_price - Get price recommendation',
            'POST /price_analysis - Get comprehensive price analysis',
            'POST /report_outcome - Report outcome (feedback)'
        ]
    })

if __name__ == '__main__':
    print("🚀 Starting Simple Price Recommendation API...")
    print("📍 Server will run on: http://localhost:5002")
    print("🏥 Health check: http://localhost:5002/health")
    
    app.run(host='0.0.0.0', port=5002, debug=False)
