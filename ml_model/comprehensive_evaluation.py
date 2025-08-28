import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from mabwiser.mab import MAB, LearningPolicy
import json
import warnings
warnings.filterwarnings('ignore')

class OfflineBanditEvaluator:
    """Comprehensive offline evaluation framework for multi-armed bandit algorithms"""
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.df = None
        self.encoder = None
        self.scaler = None
        self.feature_names = None
        self.arms = [0.9, 1.0, 1.1]
        self.results = {}
    
    def load_and_prepare_data(self):
        """Load and prepare data for evaluation"""
        print("Loading and preparing data...")
        self.df = pd.read_csv(self.data_path)
        
        # Enhanced feature engineering
        self.df = self._enhanced_feature_engineering(self.df)
        
        # Prepare features
        categorical_features = ['inventory_level', 'Market_Segment']
        numerical_features = [
            'Storage', 'RAM', 'Screen Size', 'Camera', 'Battery', 
            'market_shock', 'Backglass_Damage', 'Screen_Damage',
            'Storage_RAM_interaction', 'Battery_Age_interaction', 'Damage_Total',
            'Storage_squared', 'Battery_squared', 'Condition_Score', 'Age_Depreciation'
        ]
        
        # Encode categorical features
        self.encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        encoded_categorical = self.encoder.fit_transform(self.df[categorical_features])
        
        # Scale numerical features
        self.scaler = StandardScaler()
        scaled_numerical = self.scaler.fit_transform(self.df[numerical_features])
        
        # Combine features
        contexts = np.hstack([encoded_categorical, scaled_numerical])
        self.feature_names = list(self.encoder.get_feature_names_out(categorical_features)) + numerical_features
        
        return contexts
    
    def _enhanced_feature_engineering(self, df):
        """Enhanced feature engineering"""
        df = df.copy()
        
        # Interaction features
        df['Storage_RAM_interaction'] = df['Storage'] * df['RAM']
        df['Battery_Age_interaction'] = df['Battery'] * (100 - df['Months_since_release'])
        df['Damage_Total'] = df['Backglass_Damage'] + df['Screen_Damage']
        
        # Polynomial features
        df['Storage_squared'] = df['Storage'] ** 2
        df['Battery_squared'] = df['Battery'] ** 2
        
        # Market segmentation
        def get_market_segment(row):
            if row['Storage'] >= 512:
                return 'premium'
            elif row['Storage'] >= 256:
                return 'high_end'
            elif row['Storage'] >= 128:
                return 'mid_range'
            else:
                return 'budget'
        
        df['Market_Segment'] = df.apply(get_market_segment, axis=1)
        
        # Device condition score
        df['Condition_Score'] = (
            df['Battery'] * 0.4 +
            (1 - df['Backglass_Damage']) * 30 +
            (1 - df['Screen_Damage']) * 30
        )
        
        # Age depreciation factor
        df['Age_Depreciation'] = np.exp(-df['Months_since_release'] / 24)
        
        return df
    
    def _calculate_business_reward(self, price_tier: float, base_price: float, context_dict: dict) -> float:
        """Calculate business-oriented reward"""
        battery_health = context_dict.get('Battery', 95)
        damage_penalty = context_dict.get('Backglass_Damage', 0) + context_dict.get('Screen_Damage', 0)
        inventory = context_dict.get('inventory_level', 'decent')
        
        # Profit margins by tier
        profit_margins = {0.9: 0.15, 1.0: 0.25, 1.1: 0.35}
        
        # Sale probability
        sale_prob = 0.7
        if price_tier == 0.9:
            sale_prob = 0.9
        elif price_tier == 1.1:
            sale_prob = 0.5
        
        # Condition adjustments
        sale_prob *= (battery_health / 100) * (1 - damage_penalty * 0.2)
        
        # Inventory adjustments
        if inventory == 'high':
            sale_prob *= 1.1
        elif inventory == 'low':
            sale_prob *= 0.9
        
        # Calculate expected profit
        expected_profit = sale_prob * base_price * price_tier * profit_margins.get(price_tier, 0.25)
        holding_cost = base_price * 0.01 * (1 - sale_prob)
        
        return expected_profit - holding_cost
    
    def evaluate_algorithm(self, algorithm_name: str, learning_policy, contexts: np.ndarray, 
                          test_size: float = 0.3) -> dict:
        """Evaluate a single algorithm using historical data replay"""
        print(f"Evaluating {algorithm_name}...")
        
        # Split data
        train_contexts, test_contexts, train_idx, test_idx = train_test_split(
            contexts, range(len(contexts)), test_size=test_size, random_state=42
        )
        
        train_df = self.df.iloc[train_idx].reset_index(drop=True)
        test_df = self.df.iloc[test_idx].reset_index(drop=True)
        
        # Generate training rewards and decisions
        train_rewards = []
        train_decisions = []
        
        for idx, row in train_df.iterrows():
            context_dict = row[['Storage', 'RAM', 'Battery', 'Backglass_Damage', 
                              'Screen_Damage', 'inventory_level']].to_dict()
            optimal_tier = np.random.choice(self.arms)
            reward = self._calculate_business_reward(optimal_tier, row['Price'], context_dict)
            train_rewards.append(reward)
            train_decisions.append(optimal_tier)
        
        # Initialize and train model
        model = MAB(arms=self.arms, learning_policy=learning_policy)
        model.fit(decisions=train_decisions, rewards=train_rewards, contexts=train_contexts)
        
        # Online evaluation on test set
        cumulative_rewards = []
        cumulative_regrets = []
        arm_selections = {arm: 0 for arm in self.arms}
        
        total_reward = 0
        total_regret = 0
        
        for idx, row in test_df.iterrows():
            context = test_contexts[idx].reshape(1, -1)
            context_dict = row[['Storage', 'RAM', 'Battery', 'Backglass_Damage', 
                              'Screen_Damage', 'inventory_level']].to_dict()
            
            # Get model prediction
            predicted_arm = model.predict(context)
            arm_selections[predicted_arm] += 1
            
            # Calculate actual reward
            actual_reward = self._calculate_business_reward(predicted_arm, row['Price'], context_dict)
            
            # Calculate optimal reward (oracle)
            optimal_rewards = [
                self._calculate_business_reward(arm, row['Price'], context_dict) 
                for arm in self.arms
            ]
            optimal_reward = max(optimal_rewards)
            regret = optimal_reward - actual_reward
            
            total_reward += actual_reward
            total_regret += regret
            
            cumulative_rewards.append(total_reward)
            cumulative_regrets.append(total_regret)
            
            # Update model with feedback (online learning)
            model.partial_fit([predicted_arm], [actual_reward], context)
        
        return {
            'algorithm': algorithm_name,
            'total_reward': total_reward,
            'total_regret': total_regret,
            'avg_reward': total_reward / len(test_df),
            'avg_regret': total_regret / len(test_df),
            'cumulative_rewards': cumulative_rewards,
            'cumulative_regrets': cumulative_regrets,
            'arm_selections': arm_selections,
            'n_decisions': len(test_df)
        }
    
    def run_comparative_evaluation(self) -> dict:
        """Run comparative evaluation of multiple algorithms"""
        print("Starting comprehensive bandit evaluation...")
        
        contexts = self.load_and_prepare_data()
        
        # Define algorithms to compare
        algorithms = {
            'LinTS_Conservative': LearningPolicy.LinTS(alpha=0.5),
            'LinTS_Standard': LearningPolicy.LinTS(alpha=1.5),
            'LinTS_Aggressive': LearningPolicy.LinTS(alpha=3.0),
            'LinUCB_Conservative': LearningPolicy.LinUCB(alpha=0.5),
            'LinUCB_Standard': LearningPolicy.LinUCB(alpha=1.0),
            'EpsilonGreedy_Low': LearningPolicy.EpsilonGreedy(epsilon=0.05),
            'EpsilonGreedy_High': LearningPolicy.EpsilonGreedy(epsilon=0.1),
            'Random_Baseline': LearningPolicy.Random()
        }
        
        results = {}
        
        for name, policy in algorithms.items():
            try:
                result = self.evaluate_algorithm(name, policy, contexts)
                results[name] = result
            except Exception as e:
                print(f"Error evaluating {name}: {str(e)}")
                continue
        
        self.results = results
        return results
    
    def generate_report(self) -> str:
        """Generate a comprehensive evaluation report"""
        if not self.results:
            return "No evaluation results available. Run evaluation first."
        
        report = []
        report.append("=" * 80)
        report.append("🤖 MULTI-ARMED BANDIT EVALUATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary table
        report.append("📊 ALGORITHM PERFORMANCE SUMMARY")
        report.append("-" * 65)
        report.append(f"{'Algorithm':<25} {'Avg Reward':<12} {'Avg Regret':<12} {'Total Reward':<15}")
        report.append("-" * 65)
        
        # Sort by average reward (descending)
        sorted_results = sorted(self.results.items(), key=lambda x: x[1]['avg_reward'], reverse=True)
        
        for name, result in sorted_results:
            report.append(f"{name:<25} {result['avg_reward']:<12.2f} {result['avg_regret']:<12.2f} {result['total_reward']:<15.2f}")
        
        report.append("")
        report.append("🎯 ARM SELECTION ANALYSIS (TOP 3 ALGORITHMS)")
        report.append("-" * 65)
        
        for name, result in sorted_results[:3]:
            report.append(f"\n📈 {name}:")
            total_selections = sum(result['arm_selections'].values())
            for arm, count in result['arm_selections'].items():
                percentage = (count / total_selections) * 100 if total_selections > 0 else 0
                tier_desc = {0.9: "Discount", 1.0: "Standard", 1.1: "Premium"}
                report.append(f"   • Tier {arm} ({tier_desc[arm]}): {count:>4} selections ({percentage:>5.1f}%)")
        
        report.append("")
        report.append("🏆 KEY RECOMMENDATIONS")
        report.append("-" * 65)
        
        if sorted_results:
            best_algorithm = sorted_results[0][0]
            best_result = sorted_results[0][1]
            
            report.append(f"✅ Best Algorithm: {best_algorithm}")
            report.append(f"💰 Average Reward: {best_result['avg_reward']:.2f}")
            report.append(f"📉 Average Regret: {best_result['avg_regret']:.2f}")
            
            # Exploration-exploitation analysis
            arm_distribution = best_result['arm_selections']
            total = sum(arm_distribution.values())
            most_selected_pct = max(arm_distribution.values()) / total
            
            if most_selected_pct > 0.8:
                report.append("⚠️  WARNING: Over-exploitation detected (>80% on single arm)")
                report.append("   Consider using more explorative algorithm")
            elif most_selected_pct < 0.4:
                report.append("✨ Good exploration-exploitation balance")
            else:
                report.append("📊 Reasonable arm distribution")
            
            # Business insights
            report.append("")
            report.append("💼 BUSINESS INSIGHTS")
            report.append("-" * 65)
            
            premium_selections = arm_distribution.get(1.1, 0)
            discount_selections = arm_distribution.get(0.9, 0)
            
            if premium_selections > discount_selections:
                report.append("📈 Model favors premium pricing - indicates good market conditions")
            else:
                report.append("📉 Model favors competitive pricing - market may be price-sensitive")
            
            report.append("")
            report.append("🔧 MODEL IMPROVEMENTS")
            report.append("-" * 65)
            report.append("• Consider A/B testing with top 2-3 algorithms")
            report.append("• Monitor performance degradation over time")
            report.append("• Implement concept drift detection")
            report.append("• Add more contextual features (seasonality, competition)")
        
        return "\n".join(report)

def main():
    """Main evaluation script"""
    evaluator = OfflineBanditEvaluator('/app/data/processed_iphone_data.csv')
    
    # Run comprehensive evaluation
    print("🚀 Starting comprehensive bandit evaluation...")
    results = evaluator.run_comparative_evaluation()
    
    # Generate and print report
    report = evaluator.generate_report()
    print("\n" + report)
    
    # Save results to JSON
    print("\n💾 Saving evaluation results...")
    
    # Convert numpy arrays to lists for JSON serialization
    serializable_results = {}
    for name, result in results.items():
        serializable_results[name] = {
            k: v.tolist() if isinstance(v, np.ndarray) else v 
            for k, v in result.items()
        }
    
    with open('/app/data/bandit_evaluation_results.json', 'w') as f:
        json.dump(serializable_results, f, indent=2)
    
    print("✅ Evaluation complete!")
    print("📄 Detailed results saved to: /app/data/bandit_evaluation_results.json")
    
    # Print summary recommendations
    if results:
        best_algo = max(results.items(), key=lambda x: x[1]['avg_reward'])
        print(f"\n🏆 RECOMMENDATION: Use {best_algo[0]} for production")
        print(f"💰 Expected average reward: {best_algo[1]['avg_reward']:.2f}")

if __name__ == "__main__":
    main()
