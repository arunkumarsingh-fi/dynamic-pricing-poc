from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from mabwiser.mab import MAB, LearningPolicy
import uuid
import os

app = Flask(__name__)

pricing_bandit = None
encoder = None
feature_names = None
active_decisions = {}

def OHE(df, cats):
    enc = OneHotEncoder(handle_unknown="ignore", sparse_output=False).fit(df[cats])
    return enc

def prepare_context(enc, df, cats, extra_cols):
    A = enc.transform(df[cats])
    B = df[extra_cols].to_numpy()
    return np.hstack([A, B])

def initialize_bandit():
    global pricing_bandit, encoder, feature_names
    processed_data_path = '/app/data/processed_iphone_data.csv'
    if not os.path.exists(processed_data_path): return False

    df = pd.read_csv(processed_data_path)
    arms = [0.9, 1.0, 1.1]
    categorical_features = ['inventory_level']
    numerical_features = ['Storage', 'RAM', 'Screen Size', 'Camera', 'Battery', 'market_shock', 'Backglass_Damage', 'Screen_Damage']

    encoder = OHE(df, categorical_features)
    contexts = prepare_context(encoder, df, categorical_features, numerical_features)
    feature_names = list(encoder.get_feature_names_out(categorical_features)) + numerical_features

    df['reward'] = df['adjusted_price'] - df['Price']
    rewards = df['reward']
    decisions = [np.random.choice(arms) for _ in range(len(df))]

    pricing_bandit = MAB(arms=arms, learning_policy=LearningPolicy.LinTS(alpha=1.5))
    pricing_bandit.fit(decisions=decisions, rewards=rewards, contexts=contexts)
    print("Bandit initialized and pre-trained.")
    return True

@app.route('/recommend_price', methods=['POST'])
def recommend():
    data = request.get_json()
    input_df = pd.DataFrame([data])
    
    # Add default values for missing columns
    input_df['Backglass_Damage'] = input_df.get('Backglass_Damage', 0)
    input_df['Screen_Damage'] = input_df.get('Screen_Damage', 0)
    
    context = prepare_context(encoder, input_df, ['inventory_level'], feature_names[encoder.categories_[0].size:])
    recommendation = pricing_bandit.predict(context)
    decision_id = str(uuid.uuid4())
    active_decisions[decision_id] = {'context': context, 'arm': recommendation}
    return jsonify({'decision_id': decision_id, 'recommended_price_tier': recommendation})

@app.route('/report_outcome', methods=['POST'])
def report():
    data = request.get_json()
    decision_id = data.get('decision_id')
    reward = data.get('reward')
    decision = active_decisions.pop(decision_id, None)
    if not decision: return jsonify({'error': 'Decision ID not found'}), 404

    pricing_bandit.partial_fit(decisions=[decision['arm']], rewards=[reward], contexts=decision['context'])
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    import time
    while not initialize_bandit():
        print("Waiting for data...")
        time.sleep(5)
    app.run(host='0.0.0.0', port=5001)
