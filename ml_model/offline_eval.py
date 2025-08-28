import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder
from mabwiser.mab import MAB, LearningPolicy
import os

def OHE(df, cats):
    enc = OneHotEncoder(handle_unknown="ignore", sparse_output=False).fit(df[cats])
    return enc

def prepare_context(enc, df, cats, extra_cols):
    A = enc.transform(df[cats])
    B = df[extra_cols].to_numpy()
    return np.hstack([A, B])

df = pd.read_csv('./data/processed_iphone_data.csv')
df['reward'] = df['adjusted_price'] - df['Price']

arms = [0.9, 1.0, 1.1]
categorical_features = ['inventory_level']
numerical_features = ['Storage', 'RAM', 'Screen Size', 'Camera', 'Battery', 'market_shock']

encoder = OHE(df, categorical_features)
eval_bandit = MAB(arms=arms, learning_policy=LearningPolicy.LinTS(alpha=1.5))

# Initial fit with some bootstrap data
initial_size = min(100, len(df))
bootstrap_df = df.head(initial_size)
bootstrap_contexts = prepare_context(encoder, bootstrap_df, categorical_features, numerical_features)
bootstrap_decisions = [np.random.choice(arms) for _ in range(initial_size)]
bootstrap_rewards = bootstrap_df['reward'].values
eval_bandit.fit(decisions=bootstrap_decisions, rewards=bootstrap_rewards, contexts=bootstrap_contexts)

cumulative_rewards = []
df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)

for i, row in df_shuffled.iterrows():
    context_df = pd.DataFrame([row])
    context = prepare_context(encoder, context_df, categorical_features, numerical_features)
    decision = eval_bandit.predict(context)
    current_reward = row['reward'] if decision > 0.95 else row['reward'] * 0.5
    eval_bandit.partial_fit([decision], [current_reward], context)

    if cumulative_rewards:
        cumulative_rewards.append(cumulative_rewards[-1] + current_reward)
    else:
        cumulative_rewards.append(current_reward)

plt.figure(figsize=(12, 6))
plt.plot(cumulative_rewards)
plt.title('Bandit Offline Evaluation: Cumulative Reward Over Time')
plt.xlabel('Number of Decisions')
plt.ylabel('Total Accumulated Reward (Profit)')
plt.grid(True)
plt.savefig('./data/cumulative_reward_plot.png')
print("Evaluation plot saved to data/cumulative_reward_plot.png")
