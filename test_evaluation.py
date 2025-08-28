#!/usr/bin/env python3
import sys
import os

# Add the ml_model directory to Python path
sys.path.append('./ml_model')

# Import the evaluation framework
from comprehensive_evaluation import OfflineBanditEvaluator

def main():
    print("🚀 Testing Comprehensive Bandit Evaluation Framework")
    print("=" * 60)
    
    # Initialize evaluator
    data_path = './data/processed_iphone_data.csv'
    
    if not os.path.exists(data_path):
        print(f"❌ Error: Data file not found at {data_path}")
        print("Please ensure the processed data file exists.")
        return
    
    evaluator = OfflineBanditEvaluator(data_path)
    
    try:
        # Run the evaluation
        print("🔄 Running comparative evaluation...")
        results = evaluator.run_comparative_evaluation()
        
        # Generate report
        print("\n📊 Generating evaluation report...")
        report = evaluator.generate_report()
        
        # Print the report
        print(report)
        
        # Show quick summary
        if results:
            best_algo = max(results.items(), key=lambda x: x[1]['avg_reward'])
            print(f"\n🏆 QUICK SUMMARY")
            print(f"Best Algorithm: {best_algo[0]}")
            print(f"Performance: {best_algo[1]['avg_reward']:.2f} average reward")
            print(f"Total Algorithms Tested: {len(results)}")
        
    except Exception as e:
        print(f"❌ Error during evaluation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
