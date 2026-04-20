"""
FinNexus - Fraud Detection Model Training Script

This script:
1. Loads transaction data with 7 fraud patterns
2. Engineers fraud-detection features
3. Trains Random Forest classifier (NOT Isolation Forest - we have labels!)
4. Evaluates model with focus on recall (catching fraud)
5. Saves trained model

Fraud Types Detected:
1. Account Takeover
2. Money Mule / Layering
3. Velocity Attacks
4. Smurfing / Structuring
5. Dormant Account Reactivation
6. Ping Attack (Account Testing)
7. Sequential Escalation

Author: FinNexus Team
Date: 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
    f1_score
)
from imblearn.over_sampling import SMOTE  # Handle class imbalance
import joblib
import os
from datetime import datetime

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*70)
print("  FINNEXUS - FRAUD DETECTION MODEL TRAINING")
print("="*70)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# ==========================================
# STEP 1: LOAD DATA
# ==========================================

print(" STEP 1: Loading fraud transaction data...")

try:
    df = pd.read_csv('data/fraud_transactions.csv')
    print(f" Data loaded successfully!")
    print(f"   Shape: {df.shape[0]} rows × {df.shape[1]} columns")
except FileNotFoundError:
    print(" ERROR: data/fraud_transactions.csv not found!")
    print("   Please run data_generator.py first.")
    exit(1)

# Display sample
print("\n Sample transactions:")
print(df.head(10)[['transaction_id', 'user_id', 'amount', 'is_fraud', 'fraud_type']])

# Check fraud distribution
print("\n Fraud Distribution:")
print(df['is_fraud'].value_counts())
print(f"\n   Fraud Rate: {df['is_fraud'].mean()*100:.2f}%")

# Fraud type breakdown
if df['is_fraud'].sum() > 0:
    print("\n Fraud Type Breakdown:")
    fraud_breakdown = df[df['is_fraud']==1]['fraud_type'].value_counts()
    print(fraud_breakdown)

# ==========================================
# STEP 2: FEATURE ENGINEERING
# ==========================================

print("\n" + "="*70)
print(" STEP 2: Engineering Fraud Detection Features")
print("="*70)

# Already have derived features from generator, but let's add more

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp').reset_index(drop=True)

# Add additional engineered features

# 1. Transaction sequence features (detect escalation)
df['prev_amount'] = df.groupby('user_id')['amount'].shift(1)
df['amount_increase_ratio'] = df['amount'] / (df['prev_amount'] + 1)  # +1 to avoid division by zero
df['amount_increase_ratio'].fillna(1, inplace=True)

# 2. Ping detection: is this a micro-transaction?
df['is_micro_transaction'] = (df['amount'] < 50).astype(int)

# 3. Following micro transaction? (potential ping + drain pattern)
df['followed_micro'] = df.groupby('user_id')['is_micro_transaction'].shift(1).fillna(0).astype(int)

# 4. Time-based features
df['is_night_time'] = ((df['hour'] >= 22) | (df['hour'] <= 5)).astype(int)
df['is_weekend'] = df['timestamp'].dt.dayofweek.isin([5, 6]).astype(int)

# 5. Rapid succession flag (< 15 minutes since last tx)
df['is_rapid_succession'] = (df['time_since_last_tx_minutes'] < 15).astype(int)

# 6. Amount outlier detection (3 standard deviations from user mean)
user_amount_stats = df.groupby('user_id')['amount'].agg(['mean', 'std']).reset_index()
user_amount_stats.columns = ['user_id', 'user_mean_amount', 'user_std_amount']
df = df.merge(user_amount_stats, on='user_id', how='left')
df['is_amount_outlier'] = (
    df['amount'] > (df['user_mean_amount'] + 3 * df['user_std_amount'])
).astype(int)

print("\n Feature engineering complete!")
print(f"   Total features: {df.shape[1]}")

# Show new features
print("\n New engineered features:")
new_features = [
    'amount_increase_ratio', 'is_micro_transaction', 'followed_micro',
    'is_night_time', 'is_weekend', 'is_rapid_succession', 'is_amount_outlier'
]
for feat in new_features:
    print(f"   • {feat}")

# ==========================================
# STEP 3: PREPARE FEATURES
# ==========================================

print("\n" + "="*70)
print(" STEP 3: Preparing Features and Target")
print("="*70)

# Select features for model
feature_columns = [
    # Basic transaction features
    'amount',
    'hour',
    
    # Velocity features
    'daily_tx_count',
    'time_since_last_tx_minutes',
    'is_rapid_succession',
    
    # Amount pattern features
    'amount_deviation_ratio',
    'amount_increase_ratio',
    'is_amount_outlier',
    
    # Micro-transaction detection (ping attack)
    'is_micro_transaction',
    'followed_micro',
    
    # Behavioral flags
    'is_round_amount',
    'is_new_recipient',
    
    # Temporal features
    'is_night_time',
    'is_weekend'
]

print(f"\n Using {len(feature_columns)} features:")
for i, col in enumerate(feature_columns, 1):
    print(f"   {i:2d}. {col}")

# Separate features and target
X = df[feature_columns]
y = df['is_fraud']

print(f"\n Features matrix: {X.shape}")
print(f" Target vector: {y.shape}")

# Handle any NaN values
X = X.fillna(0)

# Check class imbalance
fraud_count = y.sum()
normal_count = len(y) - fraud_count
imbalance_ratio = normal_count / fraud_count

print(f"\n  Class Balance:")
print(f"   Normal transactions: {normal_count:,}")
print(f"   Fraud transactions:  {fraud_count:,}")
print(f"   Imbalance ratio:     {imbalance_ratio:.1f}:1")

if imbalance_ratio > 10:
    print(f"     High imbalance detected - will use SMOTE for balancing")

# ==========================================
# STEP 4: TRAIN-TEST SPLIT
# ==========================================

print("\n" + "="*70)
print("  STEP 4: Splitting Data")
print("="*70)

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y  # Maintain fraud rate in both sets
)

print(f"\n Training set: {X_train.shape[0]:,} samples")
print(f" Test set:     {X_test.shape[0]:,} samples")
print(f"\n   Training fraud rate: {y_train.mean()*100:.2f}%")
print(f"   Test fraud rate:     {y_test.mean()*100:.2f}%")

# ==========================================
# STEP 5: HANDLE CLASS IMBALANCE (SMOTE)
# ==========================================

print("\n" + "="*70)
print("  STEP 5: Balancing Classes with SMOTE")
print("="*70)

print("\n Applying SMOTE (Synthetic Minority Over-sampling)...")
print("   This creates synthetic fraud examples to balance the dataset")

# Apply SMOTE only on training data
smote = SMOTE(random_state=42, k_neighbors=5)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

print(f"\n Resampling complete!")
print(f"   Before SMOTE: {len(y_train):,} samples")
print(f"   After SMOTE:  {len(y_train_balanced):,} samples")
print(f"\n   Fraud rate before: {y_train.mean()*100:.2f}%")
print(f"   Fraud rate after:  {y_train_balanced.mean()*100:.2f}%")

# ==========================================
# STEP 6: TRAIN MODEL
# ==========================================

print("\n" + "="*70)
print(" STEP 6: Training Random Forest Classifier")
print("="*70)

print("\n🔧 Model Configuration:")
print("   • Algorithm: Random Forest")
print("   • Number of trees: 100")
print("   • Max depth: 20 (deeper for complex fraud patterns)")
print("   • Class weight: balanced")

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=20,           # Deeper trees for complex patterns
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=42,
    class_weight='balanced',  # Extra weight to fraud class
    n_jobs=-1,
    verbose=1
)

print("\n Training started...")
model.fit(X_train_balanced, y_train_balanced)
print("\n Training complete!")

# ==========================================
# STEP 7: EVALUATE MODEL
# ==========================================

print("\n" + "="*70)
print(" STEP 7: Evaluating Model Performance")
print("="*70)

# Predictions
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

# 7.1 - Classification Report
print("\n" + "-"*70)
print(" CLASSIFICATION REPORT")
print("-"*70)
print(classification_report(
    y_test,
    y_pred,
    target_names=['Normal', 'Fraud'],
    digits=3
))

# 7.2 - Confusion Matrix
print("\n" + "-"*70)
print(" CONFUSION MATRIX")
print("-"*70)

cm = confusion_matrix(y_test, y_pred)
print("\n   Actual →")
print("   Predicted ↓")
print(f"\n              Normal    Fraud")
print(f"   Normal     {cm[0][0]:6d}    {cm[0][1]:5d}")
print(f"   Fraud      {cm[1][0]:6d}    {cm[1][1]:5d}")

# Calculate key metrics
tn, fp, fn, tp = cm.ravel()

print(f"\n   True Positives (Caught fraud):  {tp}")
print(f"   False Negatives (Missed fraud): {fn}")
print(f"   False Positives (False alarms): {fp}")
print(f"   True Negatives (Correct):       {tn}")

# Critical metrics for fraud detection
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
f1 = f1_score(y_test, y_pred)

print(f"\n FRAUD DETECTION METRICS:")
print(f"   Recall (Fraud Caught):    {recall*100:.1f}% ← MOST IMPORTANT")
print(f"   Precision (Accuracy):     {precision*100:.1f}%")
print(f"   F1-Score:                 {f1:.3f}")

if recall > 0.90:
    print("    EXCELLENT: Catching >90% of fraud!")
elif recall > 0.80:
    print("   ✓  GOOD: Catching >80% of fraud")
else:
    print("     NEEDS IMPROVEMENT: Missing too much fraud")

# Visualize confusion matrix
os.makedirs('logs/plots', exist_ok=True)

plt.figure(figsize=(8, 6))
sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    cmap='Reds',
    xticklabels=['Normal', 'Fraud'],
    yticklabels=['Normal', 'Fraud']
)
plt.title('Confusion Matrix - Fraud Detection', fontsize=14, fontweight='bold')
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.tight_layout()
plt.savefig('logs/plots/fraud_01_confusion_matrix.png', dpi=150)
print("\n Saved: logs/plots/fraud_01_confusion_matrix.png")
plt.close()

# 7.3 - ROC Curve
print("\n Creating ROC curve...")

roc_auc = roc_auc_score(y_test, y_pred_proba)
fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='#FF6B6B', linewidth=2, label=f'ROC (AUC = {roc_auc:.3f})')
plt.plot([0, 1], [0, 1], 'k--', label='Random')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate (Recall)')
plt.title('ROC Curve - Fraud Detection', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('logs/plots/fraud_02_roc_curve.png', dpi=150)
print(" Saved: logs/plots/fraud_02_roc_curve.png")
plt.close()

print(f"\n   ROC-AUC: {roc_auc:.4f}")

# 7.4 - Precision-Recall Curve (More important for imbalanced data)
print("\n Creating Precision-Recall curve...")

precision_vals, recall_vals, pr_thresholds = precision_recall_curve(y_test, y_pred_proba)

plt.figure(figsize=(8, 6))
plt.plot(recall_vals, precision_vals, color='#FF6B6B', linewidth=2)
plt.xlabel('Recall (Fraud Caught)')
plt.ylabel('Precision (Accuracy of Fraud Alerts)')
plt.title('Precision-Recall Curve', fontsize=14, fontweight='bold')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('logs/plots/fraud_03_precision_recall.png', dpi=150)
print(" Saved: logs/plots/fraud_03_precision_recall.png")
plt.close()

# ==========================================
# STEP 8: FEATURE IMPORTANCE
# ==========================================

print("\n" + "="*70)
print(" STEP 8: Analyzing Feature Importance")
print("="*70)

feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n Top 10 Most Important Features for Fraud Detection:")
print(feature_importance.head(10).to_string(index=False))

# Plot
plt.figure(figsize=(10, 8))
plt.barh(
    feature_importance['feature'][:10],
    feature_importance['importance'][:10],
    color='#FF6B6B'
)
plt.xlabel('Importance')
plt.title('Top 10 Features - Fraud Detection', fontsize=14, fontweight='bold')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('logs/plots/fraud_04_feature_importance.png', dpi=150)
print("\n Saved: logs/plots/fraud_04_feature_importance.png")
plt.close()

# ==========================================
# STEP 9: FRAUD TYPE DETECTION ANALYSIS
# ==========================================

print("\n" + "="*70)
print(" STEP 9: Analyzing Detection by Fraud Type")
print("="*70)

# Get fraud samples from test set
fraud_samples = df.loc[X_test.index][y_test == 1].copy()
fraud_samples['predicted'] = y_pred[y_test == 1]
fraud_samples['prediction_prob'] = y_pred_proba[y_test == 1]

print("\n Detection Rate by Fraud Type:")
if len(fraud_samples) > 0:
    detection_by_type = fraud_samples.groupby('fraud_type').agg({
        'predicted': ['sum', 'count']
    })
    detection_by_type.columns = ['detected', 'total']
    detection_by_type['detection_rate'] = (
        detection_by_type['detected'] / detection_by_type['total'] * 100
    )
    print(detection_by_type.to_string())
    
    # Plot
    plt.figure(figsize=(10, 6))
    detection_by_type['detection_rate'].plot(kind='bar', color='#FF6B6B')
    plt.xlabel('Fraud Type')
    plt.ylabel('Detection Rate (%)')
    plt.title('Detection Rate by Fraud Type', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 100)
    plt.axhline(y=90, color='green', linestyle='--', label='90% Target')
    plt.legend()
    plt.tight_layout()
    plt.savefig('logs/plots/fraud_05_detection_by_type.png', dpi=150)
    print("\n Saved: logs/plots/fraud_05_detection_by_type.png")
    plt.close()

# ==========================================
# STEP 10: SAVE MODEL
# ==========================================

print("\n" + "="*70)
print(" STEP 10: Saving Model and Artifacts")
print("="*70)

os.makedirs('models', exist_ok=True)

# Save model
model_path = 'models/fraud_detector.pkl'
joblib.dump(model, model_path)
print(f"\n Saved model: {model_path}")
print(f"   File size: {os.path.getsize(model_path) / 1024**2:.2f} MB")

# Save feature names
feature_names_path = 'models/fraud_feature_names.pkl'
joblib.dump(feature_columns, feature_names_path)
print(f" Saved feature names: {feature_names_path}")

# Save metadata
metadata = {
    'model_type': 'RandomForestClassifier',
    'training_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'training_samples': len(X_train_balanced),
    'test_samples': len(X_test),
    'recall': float(recall),
    'precision': float(precision),
    'f1_score': float(f1),
    'roc_auc': float(roc_auc),
    'features': feature_columns,
    'fraud_types': [
        'account_takeover', 'money_mule', 'velocity_attack',
        'smurfing', 'dormant_reactivation', 'ping_attack',
        'sequential_escalation'
    ]
}

metadata_path = 'models/fraud_model_metadata.pkl'
joblib.dump(metadata, metadata_path)
print(f" Saved metadata: {metadata_path}")

# ==========================================
# STEP 11: TEST PREDICTIONS
# ==========================================

print("\n" + "="*70)
print(" STEP 11: Testing on Sample Fraud Patterns")
print("="*70)

# Get samples of each fraud type
for fraud_type in ['ping_attack', 'sequential_escalation', 'velocity_attack']:
    type_samples = fraud_samples[fraud_samples['fraud_type'] == fraud_type]
    
    if len(type_samples) > 0:
        sample = type_samples.iloc[0]
        
        print(f"\n Sample: {fraud_type.upper().replace('_', ' ')}")
        print(f"   Amount: ₹{sample['amount']:.2f}")
        print(f"   Hour: {int(sample['hour'])}:00")
        print(f"   Daily TX Count: {int(sample['daily_tx_count'])}")
        print(f"   Predicted: {' FRAUD' if sample['predicted'] == 1 else '✅ Normal'}")
        print(f"   Confidence: {sample['prediction_prob']*100:.1f}%")

# ==========================================
# FINAL SUMMARY
# ==========================================

print("\n" + "="*70)
print(" FRAUD MODEL TRAINING COMPLETE!")
print("="*70)

print(f"\n Final Performance:")
print(f"   • Recall (Fraud Caught):  {recall*100:.1f}%")
print(f"   • Precision:              {precision*100:.1f}%")
print(f"   • F1-Score:               {f1:.3f}")
print(f"   • ROC-AUC:                {roc_auc:.4f}")

print(f"\n Saved Files:")
print(f"   • Model: models/fraud_detector.pkl")
print(f"   • Features: models/fraud_feature_names.pkl")
print(f"   • Metadata: models/fraud_model_metadata.pkl")

print(f"\n Plots:")
print(f"   • logs/plots/fraud_01_confusion_matrix.png")
print(f"   • logs/plots/fraud_02_roc_curve.png")
print(f"   • logs/plots/fraud_03_precision_recall.png")
print(f"   • logs/plots/fraud_04_feature_importance.png")
print(f"   • logs/plots/fraud_05_detection_by_type.png")

print(f"\nNext Steps:")
print(f"   1. Build FastAPI service to serve predictions")
print(f"   2. Integrate with Node.js backend")
print(f"   3. Add RAG (Gemini LLM) for explanations")

print(f"\n{'='*70}")
print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*70}\n")