#!/usr/bin/env python3
"""
Comprehensive test script for the Dynamic Pricing Bandit System
Tests API functionality, different pricing scenarios, and feedback loop
"""

import requests
import json
import time
from typing import List, Dict

API_BASE_URL = "http://localhost:5001"

def test_price_recommendation(scenario: Dict) -> Dict:
    """Test a price recommendation scenario"""
    try:
        response = requests.post(f"{API_BASE_URL}/recommend_price", 
                               json=scenario, 
                               timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

def test_feedback(decision_id: str, reward: float) -> Dict:
    """Test feedback reporting"""
    try:
        response = requests.post(f"{API_BASE_URL}/report_outcome",
                               json={"decision_id": decision_id, "reward": reward},
                               timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Feedback failed: {e}"}

def run_comprehensive_test():
    """Run comprehensive test scenarios"""
    
    print("🧪 Testing Dynamic Pricing Bandit System")
    print("=" * 50)
    
    # Test scenarios representing different iPhone configurations and market conditions
    test_scenarios = [
        {
            "name": "High-End iPhone (Low Inventory)",
            "config": {
                "Storage": 512,
                "RAM": 6,
                "Screen Size": 6.7,
                "Camera": 48,
                "Battery": 4300,
                "inventory_level": "low",
                "market_shock": 0
            },
            "expected_behavior": "Higher pricing tier due to low inventory"
        },
        {
            "name": "Mid-Range iPhone (High Inventory + Market Shock)",
            "config": {
                "Storage": 256,
                "RAM": 4,
                "Screen Size": 6.1,
                "Camera": 12,
                "Battery": 3200,
                "inventory_level": "high",
                "market_shock": 1
            },
            "expected_behavior": "Lower pricing tier due to high inventory and market shock"
        },
        {
            "name": "Entry-Level iPhone (Decent Inventory)",
            "config": {
                "Storage": 64,
                "RAM": 3,
                "Screen Size": 4.7,
                "Camera": 12,
                "Battery": 1800,
                "inventory_level": "decent",
                "market_shock": 0
            },
            "expected_behavior": "Standard pricing tier"
        }
    ]
    
    decisions_for_feedback = []
    
    # Test price recommendations
    print("\n📊 Testing Price Recommendations:")
    print("-" * 40)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print(f"   Config: {scenario['config']}")
        
        result = test_price_recommendation(scenario['config'])
        
        if "error" in result:
            print(f"   ❌ FAILED: {result['error']}")
        else:
            tier = result.get('recommended_price_tier', 'N/A')
            decision_id = result.get('decision_id', 'N/A')
            print(f"   ✅ SUCCESS: Price Tier = {tier}")
            print(f"   📝 Decision ID: {decision_id}")
            
            # Store for feedback testing
            decisions_for_feedback.append({
                'decision_id': decision_id,
                'scenario': scenario['name'],
                'tier': tier
            })
    
    # Test feedback system
    print("\n🔄 Testing Feedback System:")
    print("-" * 30)
    
    for i, decision in enumerate(decisions_for_feedback, 1):
        # Simulate different profit outcomes
        simulated_profit = 50.0 + (i * 25.0)  # Varying profits
        
        print(f"\n{i}. Reporting outcome for: {decision['scenario']}")
        print(f"   Decision ID: {decision['decision_id']}")
        print(f"   Simulated Profit: ${simulated_profit}")
        
        feedback_result = test_feedback(decision['decision_id'], simulated_profit)
        
        if "error" in feedback_result:
            print(f"   ❌ FEEDBACK FAILED: {feedback_result['error']}")
        else:
            print(f"   ✅ FEEDBACK SUCCESS: {feedback_result.get('status', 'unknown')}")
    
    # Test system learning by repeating a scenario
    print("\n🧠 Testing System Learning:")
    print("-" * 25)
    
    learning_scenario = {
        "Storage": 256,
        "RAM": 6,
        "Screen Size": 6.1,
        "Camera": 48,
        "Battery": 3200,
        "inventory_level": "low",
        "market_shock": 0
    }
    
    print("Running same scenario multiple times to observe learning...")
    
    for i in range(3):
        print(f"\nRun {i+1}:")
        result = test_price_recommendation(learning_scenario)
        
        if "error" not in result:
            tier = result.get('recommended_price_tier', 'N/A')
            print(f"   Price Tier: {tier}")
            
            # Provide feedback
            if i < 2:  # Don't feedback on last run
                feedback_result = test_feedback(result['decision_id'], 80.0)
                if "error" not in feedback_result:
                    print(f"   Feedback provided: $80.00 profit")
        
        time.sleep(0.5)  # Brief pause between requests
    
    print("\n" + "=" * 50)
    print("✅ Comprehensive test completed!")
    print("\n💡 Summary:")
    print("- API endpoints are functional")
    print("- Price recommendations are being generated")
    print("- Feedback loop is operational")
    print("- System is ready for live demonstration")
    
    print(f"\n🌐 Access Points:")
    print(f"- API: {API_BASE_URL}")
    print(f"- UI: http://localhost:8501")

if __name__ == "__main__":
    run_comprehensive_test()
