#!/usr/bin/env python3
"""
Test script for the ML Price Recommendation API

This script demonstrates how to use the enhanced price recommendation API
that returns both pricing tiers and actual EUR/LKR prices.

Usage:
1. First start the Flask API server:
   python3 ml_model/price_recommendation_app.py

2. Then run this test script:
   python3 test_price_api.py

The API runs on http://localhost:5002
"""

import requests
import json
import time
import sys

# API Configuration
API_BASE_URL = "http://localhost:5002"
ENDPOINTS = {
    'recommend': f"{API_BASE_URL}/recommend_price",
    'health': f"{API_BASE_URL}/health",
    'price_analysis': f"{API_BASE_URL}/price_analysis",
    'report': f"{API_BASE_URL}/report_outcome"
}

# Sample test data representing different device configurations
TEST_DEVICES = [
    {
        "name": "iPhone 13 Pro - Premium",
        "data": {
            "Model": "iphone 13 pro",
            "Storage": 512,
            "RAM": 6,
            "Screen Size": 6.1,
            "Camera": 12,
            "Battery": 95,
            "Screen_Damage": 0,
            "Backglass_Damage": 0,
            "inventory_level": "low",
            "market_shock": 0,
            "Months_since_release": 12
        }
    },
    {
        "name": "iPhone 12 - Mid Range",
        "data": {
            "Model": "iphone 12",
            "Storage": 256,
            "RAM": 4,
            "Screen Size": 6.1,
            "Camera": 12,
            "Battery": 80,
            "Screen_Damage": 0,
            "Backglass_Damage": 1,
            "inventory_level": "decent",
            "market_shock": 0,
            "Months_since_release": 24
        }
    },
    {
        "name": "iPhone 11 - Budget with Damage",
        "data": {
            "Model": "iphone 11",
            "Storage": 128,
            "RAM": 4,
            "Screen Size": 6.1,
            "Camera": 12,
            "Battery": 70,
            "Screen_Damage": 1,
            "Backglass_Damage": 1,
            "inventory_level": "high",
            "market_shock": 1,
            "Months_since_release": 36
        }
    },
    {
        "name": "iPhone 14 Pro Max - Ultra Premium",
        "data": {
            "Model": "iphone 14 pro max",
            "Storage": 1024,
            "RAM": 8,
            "Screen Size": 6.7,
            "Camera": 48,
            "Battery": 98,
            "Screen_Damage": 0,
            "Backglass_Damage": 0,
            "inventory_level": "low",
            "market_shock": 0,
            "Months_since_release": 6
        }
    }
]

def wait_for_api(max_retries=30):
    """Wait for the API to be available"""
    print("🔄 Waiting for API to be available...")
    for i in range(max_retries):
        try:
            response = requests.get(ENDPOINTS['health'], timeout=5)
            if response.status_code == 200:
                print("✅ API is ready!")
                return True
        except requests.exceptions.ConnectionError:
            print(f"⏳ Attempt {i+1}/{max_retries}: API not ready yet...")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    print("❌ API failed to start within timeout period")
    return False

def test_health_check():
    """Test the health endpoint"""
    print("\n" + "="*60)
    print("🏥 HEALTH CHECK")
    print("="*60)
    
    try:
        response = requests.get(ENDPOINTS['health'])
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health check passed!")
            print(f"📊 Status: {health_data.get('status', 'Unknown')}")
            print(f"🤖 Models loaded: {', '.join(health_data.get('models_loaded', []))}")
            print(f"💰 Currency: {health_data.get('currency', 'N/A')}")
            print(f"📋 Active decisions: {health_data.get('total_decisions', 0)}")
            print(f"📈 Evaluation history: {health_data.get('evaluation_history_size', 0)} entries")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_price_recommendation(device_name, device_data, model_name="LinTS"):
    """Test price recommendation for a specific device"""
    print(f"\n🔮 PRICE RECOMMENDATION: {device_name}")
    print("-" * 60)
    
    # Add model preference to the request
    request_data = device_data.copy()
    request_data['model'] = model_name
    
    try:
        response = requests.post(ENDPOINTS['recommend'], json=request_data)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Recommendation successful!")
            print(f"🎯 Model used: {result.get('model_used', 'Unknown')}")
            print(f"📊 Market segment: {result.get('market_segment', 'Unknown')}")
            print(f"⚡ Condition score: {result.get('condition_score', 0):.1f}")
            
            # Recommended pricing
            print(f"\n💰 RECOMMENDED PRICING:")
            print(f"   Tier: {result.get('recommended_tier', 'N/A')}")
            print(f"   Strategy: {result.get('pricing_strategy', 'N/A')}")
            print(f"   Price EUR: €{result.get('recommended_price_eur', 0)}")
            print(f"   Price LKR: ₨{result.get('recommended_price_lkr', 0):,}")
            
            # Market value estimation
            market_value = result.get('estimated_market_value', {})
            print(f"\n📈 ESTIMATED MARKET VALUE:")
            print(f"   EUR: €{market_value.get('eur', 0)}")
            print(f"   LKR: ₨{market_value.get('lkr', 0):,}")
            
            # All pricing options
            all_options = result.get('all_pricing_options', {})
            if all_options:
                print(f"\n💼 ALL PRICING OPTIONS:")
                for tier, option in all_options.items():
                    status = "🎯 RECOMMENDED" if option.get('recommended', False) else "  "
                    print(f"   {status} Tier {tier}: €{option.get('price_eur', 0)} | ₨{option.get('price_lkr', 0):,} | {option.get('strategy', 'N/A')}")
            
            return result.get('decision_id')
        else:
            print(f"❌ Recommendation failed with status {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Recommendation error: {e}")
        return None

def test_price_analysis(device_name, device_data):
    """Test comprehensive price analysis for a device"""
    print(f"\n📊 PRICE ANALYSIS: {device_name}")
    print("-" * 60)
    
    try:
        response = requests.post(ENDPOINTS['price_analysis'], json=device_data)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Price analysis successful!")
            
            # Market value
            market_value = result.get('estimated_market_value', {})
            print(f"\n🏪 MARKET VALUE ESTIMATION:")
            print(f"   EUR: €{market_value.get('eur', 0)}")
            print(f"   LKR: ₨{market_value.get('lkr', 0):,}")
            
            # Pricing analysis for all tiers
            pricing_analysis = result.get('pricing_analysis', {})
            if pricing_analysis:
                print(f"\n💰 PRICING STRATEGY ANALYSIS:")
                for tier, option in pricing_analysis.items():
                    print(f"   {option.get('strategy', 'Unknown')} (Tier {tier}):")
                    print(f"      EUR: €{option.get('price_eur', 0)}")
                    print(f"      LKR: ₨{option.get('price_lkr', 0):,}")
            
            return True
        else:
            print(f"❌ Price analysis failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Price analysis error: {e}")
        return False

def test_different_models():
    """Test different ML models with the same device"""
    print("\n" + "="*60)
    print("🤖 TESTING DIFFERENT ML MODELS")
    print("="*60)
    
    test_device = TEST_DEVICES[0]  # Use the first device for model comparison
    models = ['LinTS', 'LinUCB', 'EpsilonGreedy']
    
    results = {}
    for model in models:
        print(f"\n🔬 Testing model: {model}")
        decision_id = test_price_recommendation(
            f"{test_device['name']} ({model})", 
            test_device['data'], 
            model
        )
        if decision_id:
            results[model] = decision_id
    
    return results

def demonstrate_api_workflow():
    """Demonstrate the complete API workflow"""
    print("\n" + "="*80)
    print("🚀 ML PRICE RECOMMENDATION API DEMONSTRATION")
    print("="*80)
    
    # Wait for API to be ready
    if not wait_for_api():
        print("❌ Cannot proceed without API availability")
        return False
    
    # Test health check
    if not test_health_check():
        print("❌ Health check failed, cannot proceed")
        return False
    
    print("\n" + "="*60)
    print("💰 PRICE RECOMMENDATIONS FOR DIFFERENT DEVICES")
    print("="*60)
    
    decision_ids = []
    
    # Test each device
    for device in TEST_DEVICES:
        decision_id = test_price_recommendation(device['name'], device['data'])
        if decision_id:
            decision_ids.append(decision_id)
    
    # Test price analysis
    print("\n" + "="*60)
    print("📈 COMPREHENSIVE PRICE ANALYSIS")
    print("="*60)
    
    for device in TEST_DEVICES[:2]:  # Test first two devices
        test_price_analysis(device['name'], device['data'])
    
    # Test different models
    test_different_models()
    
    print("\n" + "="*60)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*60)
    
    print(f"📋 Generated {len(decision_ids)} pricing decisions")
    print("🎯 All major API endpoints tested successfully!")
    
    # Show API usage instructions
    show_api_usage_instructions()
    
    return True

def show_api_usage_instructions():
    """Show detailed API usage instructions"""
    print("\n" + "="*60)
    print("📚 API USAGE INSTRUCTIONS")
    print("="*60)
    
    print("\n🌐 Base URL: http://localhost:5002")
    
    print("\n📍 Available Endpoints:")
    print("   GET  /health                - Health check and system status")
    print("   POST /recommend_price       - Get price recommendation")
    print("   POST /price_analysis       - Comprehensive price analysis")
    print("   POST /report_outcome       - Report actual outcome for learning")
    
    print("\n📝 Example cURL commands:")
    print("\n1. Health Check:")
    print("   curl -X GET http://localhost:5002/health")
    
    print("\n2. Price Recommendation:")
    print('   curl -X POST http://localhost:5002/recommend_price \\')
    print('        -H "Content-Type: application/json" \\')
    print('        -d \'{')
    print('              "Model": "iphone 13",')
    print('              "Storage": 256,')
    print('              "RAM": 6,')
    print('              "Screen Size": 6.1,')
    print('              "Camera": 12,')
    print('              "Battery": 90,')
    print('              "Screen_Damage": 0,')
    print('              "Backglass_Damage": 0,')
    print('              "inventory_level": "decent",')
    print('              "market_shock": 0,')
    print('              "Months_since_release": 12,')
    print('              "model": "LinTS"')
    print('            }\'')
    
    print("\n3. Price Analysis:")
    print('   curl -X POST http://localhost:5002/price_analysis \\')
    print('        -H "Content-Type: application/json" \\')
    print('        -d \'{"Model": "iphone 13", "Storage": 256, "RAM": 6, ...}\'')

def main():
    """Main function to run the API test demonstration"""
    print("🎉 Welcome to the ML Price Recommendation API Test Suite!")
    print("This script will demonstrate all the API capabilities.")
    
    # Check if user wants to proceed
    print("\nMake sure the Flask API server is running on port 5002.")
    print("You can start it with: python3 ml_model/price_recommendation_app.py")
    
    user_input = input("\nPress Enter to continue or 'q' to quit: ").strip().lower()
    if user_input == 'q':
        print("👋 Goodbye!")
        return
    
    # Run the demonstration
    success = demonstrate_api_workflow()
    
    if success:
        print("\n🎊 Test suite completed successfully!")
        print("You can now use these examples to integrate the API into your applications.")
    else:
        print("\n⚠️  Some tests failed. Please check the API server and try again.")

if __name__ == "__main__":
    main()
