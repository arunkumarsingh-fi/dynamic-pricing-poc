from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from mabwiser.mab import MAB, LearningPolicy
import uuid
import os
import json
import time
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Global variables for different models
models = {}
encoder = None
scaler = None
feature_names = None
active_decisions = {}
evaluation_history = []

class ModelEvaluator:
    def __init__(self):
        self.metrics = {
            'cumulative_regret': [],
            'reward_history': [],
            'arm_selections': {},
            'context_reward_map': {}
        }
    
    def calculate_regret(self, optimal_reward, actual_reward):
        """Calculate regret for this decision"""
        regret = optimal_reward - actual_reward
        self.metrics['cumulative_regret'].append(regret)
        return regret
    
    def update_metrics(self, arm, reward, context_hash):
        """Update evaluation metrics"""
        self.metrics['reward_history'].append(reward)
        
        if arm not in self.metrics['arm_selections']:
            self.metrics['arm_selections'][arm] = 0
        self.metrics['arm_selections'][arm] += 1
        
        if context_hash not in self.metrics['context_reward_map']:
            self.metrics['context_reward_map'][context_hash] = []
        self.metrics['context_reward_map'][context_hash].append(reward)

# Initialize evaluator
evaluator = ModelEvaluator()

def enhanced_feature_engineering(df):
    """Create advanced features for better model performance"""
    df = df.copy()
    
    # Interaction features
    df['Storage_RAM_interaction'] = df['Storage'] * df['RAM']
    df['Battery_Age_interaction'] = df['Battery'] * (100 - df['Months_since_release'])
    df['Damage_Total'] = df['Backglass_Damage'] + df['Screen_Damage']
    
    # Polynomial features for key specs
    df['Storage_squared'] = df['Storage'] ** 2
    df['Battery_squared'] = df['Battery'] ** 2
    
    # Market segment features
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
    df['Age_Depreciation'] = np.exp(-df['Months_since_release'] / 24)  # 2-year half-life
    
    return df

def calculate_business_reward(price_tier, base_price, context):
    """Calculate business-oriented reward function"""
    # Simulate actual sale probability and profit margins
    battery_health = context.get('Battery', 95)
    damage_penalty = context.get('Backglass_Damage', 0) + context.get('Screen_Damage', 0)
    inventory = context.get('inventory_level', 'decent')
    
    # Base profit margins by tier
    profit_margins = {0.9: 0.15, 1.0: 0.25, 1.1: 0.35}
    
    # Sale probability adjustments
    sale_prob = 0.7  # Base sale probability
    
    if price_tier == 0.9:  # Discount
        sale_prob = 0.9
    elif price_tier == 1.1:  # Premium
        sale_prob = 0.5
        
    # Adjust for condition
    sale_prob *= (battery_health / 100) * (1 - damage_penalty * 0.2)
    
    # Adjust for inventory
    if inventory == 'high':
        sale_prob *= 1.1  # Higher chance to sell excess inventory
    elif inventory == 'low':
        sale_prob *= 0.9  # Less pressure to sell
    
    # Calculate expected profit
    expected_profit = sale_prob * base_price * price_tier * profit_margins.get(price_tier, 0.25)
    
    # Add holding cost penalty
    holding_cost = base_price * 0.01 * (1 - sale_prob)  # 1% of value per period
    
    return expected_profit - holding_cost

def initialize_models():
    """Initialize multiple bandit algorithms for comparison"""
    global models, encoder, scaler, feature_names
    
    processed_data_path = '/app/data/processed_iphone_data.csv'
    if not os.path.exists(processed_data_path):
        return False

    df = pd.read_csv(processed_data_path)
    
    # Enhanced feature engineering
    df = enhanced_feature_engineering(df)
    
    arms = [0.9, 1.0, 1.1]
    categorical_features = ['inventory_level', 'Market_Segment']
    numerical_features = [
        'Storage', 'RAM', 'Screen Size', 'Camera', 'Battery', 
        'market_shock', 'Backglass_Damage', 'Screen_Damage',
        'Storage_RAM_interaction', 'Battery_Age_interaction', 'Damage_Total',
        'Storage_squared', 'Battery_squared', 'Condition_Score', 'Age_Depreciation'
    ]

    # Prepare features
    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    encoded_categorical = encoder.fit_transform(df[categorical_features])
    
    scaler = StandardScaler()
    scaled_numerical = scaler.fit_transform(df[numerical_features])
    
    contexts = np.hstack([encoded_categorical, scaled_numerical])
    feature_names = list(encoder.get_feature_names_out(categorical_features)) + numerical_features

    # Calculate business-oriented rewards
    rewards = []
    decisions = []
    
    for idx, row in df.iterrows():
        context_dict = row[numerical_features + ['inventory_level']].to_dict()
        optimal_tier = np.random.choice(arms)  # Simulate optimal decision
        
        reward = calculate_business_reward(optimal_tier, row['Price'], context_dict)
        rewards.append(reward)
        decisions.append(optimal_tier)

    # Initialize different bandit algorithms
    algorithms = {
        'LinTS': LearningPolicy.LinTS(alpha=1.5),
        'UCB': LearningPolicy.LinUCB(alpha=0.5),
        'EpsilonGreedy': LearningPolicy.EpsilonGreedy(epsilon=0.1),
        'ThompsonSampling': LearningPolicy.LinTS(alpha=2.0)
    }
    
    for name, policy in algorithms.items():
        model = MAB(arms=arms, learning_policy=policy)
        model.fit(decisions=decisions, rewards=rewards, contexts=contexts)
        models[name] = model
    
    print(f"Initialized {len(models)} bandit models with enhanced features.")
    return True

@app.route('/recommend_price', methods=['POST'])
def recommend():
    """Enhanced recommendation with model comparison"""
    data = request.get_json()
    model_name = data.get('model', 'LinTS')  # Allow model selection
    
    if model_name not in models:
        return jsonify({'error': f'Model {model_name} not available'}), 400
    
    # Prepare input features
    input_df = pd.DataFrame([data])
    input_df = enhanced_feature_engineering(input_df)
    
    # Extract categorical and numerical features
    categorical_features = ['inventory_level', 'Market_Segment']
    numerical_features = [
        'Storage', 'RAM', 'Screen Size', 'Camera', 'Battery', 
        'market_shock', 'Backglass_Damage', 'Screen_Damage',
        'Storage_RAM_interaction', 'Battery_Age_interaction', 'Damage_Total',
        'Storage_squared', 'Battery_squared', 'Condition_Score', 'Age_Depreciation'
    ]
    
    # Handle missing Market_Segment
    if 'Market_Segment' not in input_df.columns:
        storage = data.get('Storage', 128)
        if storage >= 512:
            input_df['Market_Segment'] = 'premium'
        elif storage >= 256:
            input_df['Market_Segment'] = 'high_end'
        elif storage >= 128:
            input_df['Market_Segment'] = 'mid_range'
        else:
            input_df['Market_Segment'] = 'budget'
    
    # Prepare context
    encoded_categorical = encoder.transform(input_df[categorical_features])
    scaled_numerical = scaler.transform(input_df[numerical_features])
    context = np.hstack([encoded_categorical, scaled_numerical])
    
    # Get prediction from selected model
    recommendation = models[model_name].predict(context)
    
    # Calculate confidence scores for all arms
    arm_probs = {}
    if hasattr(models[model_name], 'predict_expectations'):
        expectations = models[model_name].predict_expectations(context)
        total = sum(expectations.values())
        arm_probs = {str(k): v/total for k, v in expectations.items()}
    
    decision_id = str(uuid.uuid4())
    context_hash = hash(str(context.tolist()))
    
    active_decisions[decision_id] = {
        'context': context,
        'context_hash': context_hash,
        'arm': recommendation,
        'model': model_name,
        'timestamp': datetime.now().isoformat(),
        'input_data': data
    }
    
    return jsonify({
        'decision_id': decision_id,
        'recommended_price_tier': float(recommendation),
        'model_used': model_name,
        'confidence_scores': arm_probs,
        'market_segment': input_df['Market_Segment'].iloc[0],
        'condition_score': float(input_df['Condition_Score'].iloc[0])
    })

@app.route('/report_outcome', methods=['POST'])
def report():
    """Enhanced outcome reporting with evaluation metrics"""
    data = request.get_json()
    decision_id = data.get('decision_id')
    reward = data.get('reward')
    
    if decision_id not in active_decisions:
        return jsonify({'error': 'Decision ID not found'}), 404
    
    decision = active_decisions.pop(decision_id)
    model_name = decision['model']
    
    # Update the specific model that made the decision
    models[model_name].partial_fit(
        decisions=[decision['arm']], 
        rewards=[reward], 
        contexts=decision['context']
    )
    
    # Update evaluation metrics
    evaluator.update_metrics(decision['arm'], reward, decision['context_hash'])
    
    # Store evaluation history
    evaluation_entry = {
        'timestamp': datetime.now().isoformat(),
        'decision_id': decision_id,
        'model': model_name,
        'arm': float(decision['arm']),
        'reward': reward,
        'context_hash': decision['context_hash']
    }
    evaluation_history.append(evaluation_entry)
    
    return jsonify({'status': 'success', 'model_updated': model_name})

@app.route('/model_comparison', methods=['GET'])
def model_comparison():
    """Compare performance of different models"""
    if not evaluation_history:
        return jsonify({'error': 'No evaluation data available'})
    
    df = pd.DataFrame(evaluation_history)
    
    comparison = {}
    for model_name in models.keys():
        model_data = df[df['model'] == model_name]
        if len(model_data) > 0:
            comparison[model_name] = {
                'total_decisions': len(model_data),
                'average_reward': float(model_data['reward'].mean()),
                'reward_std': float(model_data['reward'].std()),
                'arm_distribution': model_data['arm'].value_counts().to_dict()
            }
    
    return jsonify({
        'model_comparison': comparison,
        'total_evaluations': len(evaluation_history),
        'overall_metrics': {
            'cumulative_regret': sum(evaluator.metrics['cumulative_regret']),
            'average_reward': np.mean(evaluator.metrics['reward_history']) if evaluator.metrics['reward_history'] else 0
        }
    })

@app.route('/feature_importance', methods=['GET'])
def feature_importance():
    """Get feature importance from LinTS model"""
    model_name = request.args.get('model', 'LinTS')
    
    if model_name not in models:
        return jsonify({'error': f'Model {model_name} not available'})
    
    # For LinTS, we can approximate feature importance from the posterior
    if hasattr(models[model_name], 'learning_policy'):
        policy = models[model_name].learning_policy
        if hasattr(policy, 'A') and hasattr(policy, 'b'):
            # Calculate approximate feature importance
            importance_scores = {}
            for i, feature in enumerate(feature_names):
                # Simple approximation - could be enhanced with proper calculation
                importance_scores[feature] = float(np.abs(np.mean([
                    policy.b[arm][i] / (policy.A[arm][i,i] + 1e-6) 
                    for arm in policy.A.keys() if i < len(policy.b[arm])
                ])))
    
            # Normalize to percentages
            total = sum(importance_scores.values())
            if total > 0:
                importance_scores = {k: (v/total)*100 for k, v in importance_scores.items()}
    
            return jsonify({
                'model': model_name,
                'feature_importance': dict(sorted(importance_scores.items(), 
                                                key=lambda x: x[1], reverse=True)[:10])
            })
    
    return jsonify({'error': 'Feature importance not available for this model'})

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': list(models.keys()),
        'total_decisions': len(active_decisions),
        'evaluation_history_size': len(evaluation_history)
    })

if __name__ == '__main__':
    import time
    while not initialize_models():
        print("Waiting for data...")
        time.sleep(5)
    app.run(host='0.0.0.0', port=5001)
