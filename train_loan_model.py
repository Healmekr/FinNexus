"""
FinNexus - Loan Approval Model Training Script

This script:
1. Loads loan application data
2. Performs exploratory data analysis (EDA)
3. Trains a Random Forest classifier
4. Evaluates model performance
5. Saves the trained model and explainer


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
    accuracy_score
)
import shap
import joblib
import os
from datetime import datetime

# Configure matplotlib for better plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*70)
print(" FINNEXUS - LOAN APPROVAL MODEL TRAINING")
print("="*70)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# ==========================================
# STEP 1: LOAD DATA
# ==========================================

print(" STEP 1: Loading data...")

# Load the dataset
try:
    df = pd.read_csv('data/loan_applications.csv')
    print(f" Data loaded successfully!")
    print(f"   Shape: {df.shape[0]} rows × {df.shape[1]} columns")
except FileNotFoundError:
    print(" ERROR: data/loan_applications.csv not found!")
    print("   Please run data_generator.py first.")
    exit(1)

# Display first few rows
print("\n First 5 rows:")
print(df.head())

# Basic info
print("\n Dataset Info:")
print(f"   Total samples: {len(df)}")
print(f"   Features: {df.shape[1]}")
print(f"   Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# Check for missing values
missing = df.isnull().sum()
if missing.sum() > 0:
    print(f"\n Missing values found:")
    print(missing[missing > 0])
else:
    print(f"\n No missing values")

# Target distribution
print("\n Target Distribution (Approved/Rejected):")
print(df['approved'].value_counts())
print(f"\n   Approval Rate: {df['approved'].mean()*100:.2f}%")

# ==========================================
# STEP 2: EXPLORATORY DATA ANALYSIS (EDA)
# ==========================================

print("\n" + "="*70)
print("STEP 2: Exploratory Data Analysis")
print("="*70)

# Create output folder for plots
os.makedirs('logs/plots', exist_ok=True)

# 2.1 - Approval Distribution
print("\nCreating approval distribution plot...")
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Count plot
df['approved'].value_counts().plot(
    kind='bar',
    ax=axes[0],
    color=['#FF6B6B', '#4ECDC4']
)
axes[0].set_title('Loan Approval Distribution', fontsize=14, fontweight='bold')
axes[0].set_xlabel('Status')
axes[0].set_ylabel('Count')
axes[0].set_xticklabels(['Rejected (0)', 'Approved (1)'], rotation=0)

# Pie chart
df['approved'].value_counts().plot(
    kind='pie',
    ax=axes[1],
    autopct='%1.1f%%',
    colors=['#FF6B6B', '#4ECDC4'],
    labels=['Rejected', 'Approved']
)
axes[1].set_ylabel('')
axes[1].set_title('Approval Rate', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('logs/plots/01_approval_distribution.png', dpi=150, bbox_inches='tight')
print("    Saved: logs/plots/01_approval_distribution.png")
plt.close()

# 2.2 - Feature Distributions by Approval Status
print("\n Creating feature distribution plots...")

key_features = ['monthly_income', 'savings_rate', 'emi_to_income_ratio', 'debt_to_income_ratio']
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.ravel()

for idx, feature in enumerate(key_features):
    # Plot distributions for approved vs rejected
    df[df['approved']==0][feature].hist(
        bins=40,
        alpha=0.6,
        label='Rejected',
        color='#FF6B6B',
        ax=axes[idx]
    )
    df[df['approved']==1][feature].hist(
        bins=40,
        alpha=0.6,
        label='Approved',
        color='#4ECDC4',
        ax=axes[idx]
    )
    
    axes[idx].set_title(f'{feature.replace("_", " ").title()}', fontsize=12, fontweight='bold')
    axes[idx].set_xlabel(feature)
    axes[idx].set_ylabel('Frequency')
    axes[idx].legend()

plt.tight_layout()
plt.savefig('logs/plots/02_feature_distributions.png', dpi=150, bbox_inches='tight')
print("   Saved: logs/plots/02_feature_distributions.png")
plt.close()

# 2.3 - Correlation Matrix
print("\n Creating correlation matrix...")

# Select numerical features for correlation
numerical_features = [
    'monthly_income', 'loan_to_income_ratio', 'savings_rate',
    'debt_to_income_ratio', 'emi_to_income_ratio',
    'account_age_months', 'transaction_count', 'approved'
]

correlation_matrix = df[numerical_features].corr()

# Plot heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(
    correlation_matrix,
    annot=True,
    fmt='.2f',
    cmap='coolwarm',
    center=0,
    square=True,
    linewidths=1,
    cbar_kws={"shrink": 0.8}
)
plt.title('Feature Correlation Matrix', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('logs/plots/03_correlation_matrix.png', dpi=150, bbox_inches='tight')
print("    Saved: logs/plots/03_correlation_matrix.png")
plt.close()

# Print correlation with target
print("\n Correlation with Approval Decision:")
correlations = correlation_matrix['approved'].sort_values(ascending=False)
print(correlations)

# ==========================================
# STEP 3: PREPARE FEATURES AND TARGET
# ==========================================

print("\n" + "="*70)
print(" STEP 3: Preparing features and target")
print("="*70)

# Define feature columns (what the model will learn from)
feature_columns = [
    'monthly_income',            # User's monthly income
    'loan_to_income_ratio',      # Loan amount / income
    'avg_monthly_savings',       # Average savings per month
    'savings_rate',              # Savings / income
    'savings_consistency',       # How stable is saving behavior
    'avg_monthly_spending',      # Average spending per month
    'spending_volatility',       # How erratic is spending
    'transaction_count',         # Number of transactions
    'avg_transaction_size',      # Average transaction amount
    'debt_to_income_ratio',      # Existing debt / income
    'account_age_months',        # How long customer has been with us
    'emi_to_income_ratio',       # EMI / income (affordability)
    'loan_amount',               # How much they want to borrow
    'loan_tenure',               # Repayment period (months)
    'loan_purpose_encoded'       # Why they need the loan (1-5)
]

print(f"\n Using {len(feature_columns)} features:")
for i, col in enumerate(feature_columns, 1):
    print(f"   {i:2d}. {col}")

# Separate features (X) and target (y)
X = df[feature_columns]
y = df['approved']

print(f"\n Features matrix: {X.shape}")
print(f"Target vector: {y.shape}")

# Check for any NaN or infinite values
if X.isnull().sum().sum() > 0:
    print("\n Found NaN values, filling with median...")
    X = X.fillna(X.median())

if np.isinf(X.values).sum() > 0:
    print("\n  Found infinite values, replacing with median...")
    X = X.replace([np.inf, -np.inf], np.nan).fillna(X.median())

print(" Data cleaned and ready for training")

# ==========================================
# STEP 4: TRAIN-TEST SPLIT
# ==========================================

print("\n" + "="*70)
print("  STEP 4: Splitting data into train and test sets")
print("="*70)

# Split: 80% training, 20% testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,        # 20% for testing
    random_state=42,       # Same seed = same split every time
    stratify=y             # Keep same approval rate in both sets
)

print(f"\n Training set: {X_train.shape[0]} samples ({X_train.shape[0]/len(X)*100:.1f}%)")
print(f" Test set:     {X_test.shape[0]} samples ({X_test.shape[0]/len(X)*100:.1f}%)")

print(f"\n Training set approval rate: {y_train.mean()*100:.2f}%")
print(f" Test set approval rate:     {y_test.mean()*100:.2f}%")

# Save processed data
os.makedirs('data/processed', exist_ok=True)
train_df = X_train.copy()
train_df['approved'] = y_train
train_df.to_csv('data/processed/loan_train.csv', index=False)

test_df = X_test.copy()
test_df['approved'] = y_test
test_df.to_csv('data/processed/loan_test.csv', index=False)

print("\n Saved processed data:")
print("    data/processed/loan_train.csv")
print("   data/processed/loan_test.csv")

# ==========================================
# STEP 5: TRAIN RANDOM FOREST MODEL
# ==========================================

print("\n" + "="*70)
print(" STEP 5: Training Random Forest Classifier")
print("="*70)

print("\n Model Configuration:")
print("   • Algorithm: Random Forest")
print("   • Number of trees: 100")
print("   • Max depth: 15")
print("   • Min samples split: 20")
print("   • Class weight: balanced (handles imbalance)")

# Initialize model
model = RandomForestClassifier(
    n_estimators=100,        # Number of decision trees
    max_depth=15,            # Maximum depth of each tree
    min_samples_split=20,    # Minimum samples to split a node
    min_samples_leaf=10,     # Minimum samples in leaf node
    random_state=42,         # Reproducibility
    class_weight='balanced', # Handle class imbalance automatically
    n_jobs=-1,               # Use all CPU cores
    verbose=1                # Show progress
)

print("\n Training started...")
print("   This may take 30-60 seconds...")

# Train the model
model.fit(X_train, y_train)

print("\n Training complete!")

# ==========================================
# STEP 6: EVALUATE MODEL
# ==========================================

print("\n" + "="*70)
print(" STEP 6: Evaluating Model Performance")
print("="*70)

# Make predictions
print("\n Making predictions on test set...")
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]  # Probability of approval

# 6.1 - Classification Report
print("\n" + "-"*70)
print(" CLASSIFICATION REPORT")
print("-"*70)
report = classification_report(
    y_test,
    y_pred,
    target_names=['Rejected', 'Approved'],
    digits=3
)
print(report)

# 6.2 - Confusion Matrix
print("\n" + "-"*70)
print(" CONFUSION MATRIX")
print("-"*70)

cm = confusion_matrix(y_test, y_pred)
print("\n   Actual →")
print("   Predicted ↓")
print(f"\n              Rejected  Approved")
print(f"   Rejected      {cm[0][0]:4d}      {cm[0][1]:4d}")
print(f"   Approved      {cm[1][0]:4d}      {cm[1][1]:4d}")

# Visualize confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    cmap='Blues',
    xticklabels=['Rejected', 'Approved'],
    yticklabels=['Rejected', 'Approved'],
    cbar_kws={'label': 'Count'}
)
plt.title('Confusion Matrix', fontsize=14, fontweight='bold')
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.tight_layout()
plt.savefig('logs/plots/04_confusion_matrix.png', dpi=150, bbox_inches='tight')
print("\n    Saved: logs/plots/04_confusion_matrix.png")
plt.close()

# 6.3 - Key Metrics
print("\n" + "-"*70)
print(" KEY METRICS")
print("-"*70)

accuracy = accuracy_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_pred_proba)

print(f"\n   Accuracy:  {accuracy*100:.2f}%")
print(f"   ROC-AUC:   {roc_auc:.4f}")

# Interpretation
if accuracy > 0.85:
    print("\n    EXCELLENT: Model performs very well!")
elif accuracy > 0.75:
    print("\n   ✓  GOOD: Model performs adequately")
else:
    print("\n    NEEDS IMPROVEMENT: Consider tuning hyperparameters")

if roc_auc > 0.90:
    print("    EXCELLENT: Strong discrimination ability")
elif roc_auc > 0.80:
    print("   ✓  GOOD: Decent discrimination")
else:
    print("     NEEDS IMPROVEMENT: Model struggles to distinguish classes")

# 6.4 - ROC Curve
print("\n Creating ROC curve...")

fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='#2D5BFF', linewidth=2, label=f'ROC Curve (AUC = {roc_auc:.3f})')
plt.plot([0, 1], [0, 1], color='gray', linestyle='--', label='Random Guess')
plt.xlabel('False Positive Rate', fontsize=12)
plt.ylabel('True Positive Rate', fontsize=12)
plt.title('ROC Curve - Loan Approval Model', fontsize=14, fontweight='bold')
plt.legend(loc='lower right', fontsize=11)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('logs/plots/05_roc_curve.png', dpi=150, bbox_inches='tight')
print("    Saved: logs/plots/05_roc_curve.png")
plt.close()

# ==========================================
# STEP 7: FEATURE IMPORTANCE
# ========================================== 

print("\n" + "="*70)
print("STEP 7: Analyzing Feature Importance")
print("="*70)

# Get feature importance
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n Top 10 Most Important Features:")
print(feature_importance.head(10).to_string(index=False))

# Plot feature importance
plt.figure(figsize=(10, 8))
plt.barh(
    feature_importance['feature'][:10],
    feature_importance['importance'][:10],
    color='#2D5BFF'
)
plt.xlabel('Importance', fontsize=12)
plt.title('Top 10 Features - Importance in Loan Approval', fontsize=14, fontweight='bold')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('logs/plots/06_feature_importance.png', dpi=150, bbox_inches='tight')
print("\n Saved: logs/plots/06_feature_importance.png")
plt.close()

# ==========================================
# STEP 8: CREATE SHAP EXPLAINER
# ==========================================

print("\n" + "="*70)
print(" STEP 8: Creating SHAP Explainer (Interpretability)")
print("="*70)

print("\n Initializing SHAP TreeExplainer...")
print("   This may take 1-2 minutes...")

# Create SHAP explainer
explainer = shap.TreeExplainer(model)

print(" Explainer created!")

# Calculate SHAP values for a sample
print("\n Calculating SHAP values for test samples...")
print("   Computing for 100 samples (representative)...")

# Use a subset for faster computation
sample_size = min(100, len(X_test))
X_sample = X_test.iloc[:sample_size]

raw_shap_values = explainer.shap_values(X_sample)

# BULLETPROOF SHAPE HANDLING:
# Extracts the "Approved" class correctly whether SHAP returns a list or a 3D array
if isinstance(raw_shap_values, list):
    plot_values = raw_shap_values[1]
elif len(np.array(raw_shap_values).shape) == 3:
    plot_values = np.array(raw_shap_values)[:, :, 1]
else:
    plot_values = raw_shap_values

print(" SHAP values calculated!")

# Plot SHAP summary
print("\nCreating SHAP summary plot...")

plt.figure(figsize=(10, 8))
shap.summary_plot(
    plot_values,  # <--- Using the safely extracted values
    X_sample,
    feature_names=feature_columns,
    show=False,
    max_display=10
)
plt.title('SHAP Feature Impact Summary', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('logs/plots/07_shap_summary.png', dpi=150, bbox_inches='tight')
print("    Saved: logs/plots/07_shap_summary.png")
plt.close()
# ==========================================
# STEP 9: SAVE MODEL AND ARTIFACTS
# ==========================================

print("\n" + "="*70)
print("STEP 9: Saving Model and Artifacts")
print("="*70)

# Create models folder if doesn't exist
os.makedirs('models', exist_ok=True)

# Save the trained model
model_path = 'models/loan_classifier.pkl'
joblib.dump(model, model_path)
print(f"\n Saved model: {model_path}")
print(f"   File size: {os.path.getsize(model_path) / 1024**2:.2f} MB")

# Save SHAP explainer
explainer_path = 'models/shap_explainer.pkl'
joblib.dump(explainer, explainer_path)
print(f"Saved explainer: {explainer_path}")
print(f"   File size: {os.path.getsize(explainer_path) / 1024**2:.2f} MB")

# Save feature names
feature_names_path = 'models/feature_names.pkl'
joblib.dump(feature_columns, feature_names_path)
print(f"Saved feature names: {feature_names_path}")

# Save model metadata
metadata = {
    'model_type': 'RandomForestClassifier',
    'n_estimators': 100,
    'training_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'training_samples': len(X_train),
    'test_samples': len(X_test),
    'accuracy': float(accuracy),
    'roc_auc': float(roc_auc),
    'features': feature_columns,
    'target_classes': ['Rejected', 'Approved']
}

metadata_path = 'models/loan_model_metadata.pkl'
joblib.dump(metadata, metadata_path)
print(f"Saved metadata: {metadata_path}")

# ==========================================
# STEP 10: TEST PREDICTIONS
# ==========================================

print("\n" + "="*70)
print("STEP 10: Testing Predictions on Sample Data")
print("="*70)

# Get a sample approved and rejected case
approved_sample = X_test[y_test == 1].iloc[0:1]
rejected_sample = X_test[y_test == 0].iloc[0:1]

print("\n" + "-"*70)
print("SAMPLE 1: Should be APPROVED")
print("-"*70)

pred_approved = model.predict(approved_sample)[0]
prob_approved = model.predict_proba(approved_sample)[0]

print(f"\n   Prediction: {'APPROVED' if pred_approved == 1 else '❌ REJECTED'}")
print(f"   Confidence: {prob_approved[1]*100:.1f}%")
print(f"\n   Key features:")
for col in ['monthly_income', 'emi_to_income_ratio', 'savings_rate', 'debt_to_income_ratio']:
    print(f"      • {col}: {approved_sample[col].values[0]:.4f}")

print("\n" + "-"*70)
print("SAMPLE 2: Should be REJECTED")
print("-"*70)

pred_rejected = model.predict(rejected_sample)[0]
prob_rejected = model.predict_proba(rejected_sample)[0]

print(f"\n   Prediction: {'APPROVED' if pred_rejected == 1 else '❌ REJECTED'}")
print(f"   Confidence: {prob_rejected[0]*100:.1f}%")
print(f"\n   Key features:")
for col in ['monthly_income', 'emi_to_income_ratio', 'savings_rate', 'debt_to_income_ratio']:
    print(f"      • {col}: {rejected_sample[col].values[0]:.4f}")

# ==========================================
# FINAL SUMMARY
# ==========================================

print("\n" + "="*70)
print("TRAINING COMPLETE!")
print("="*70)

print(f"\nFinal Model Performance:")
print(f"   • Accuracy:  {accuracy*100:.2f}%")
print(f"   • ROC-AUC:   {roc_auc:.4f}")
print(f"   • Training samples: {len(X_train)}")
print(f"   • Test samples: {len(X_test)}")

print(f"\nSaved Files:")
print(f"   • Model: models/loan_classifier.pkl")
print(f"   • Explainer: models/shap_explainer.pkl")
print(f"   • Feature names: models/feature_names.pkl")
print(f"   • Metadata: models/loan_model_metadata.pkl")

print(f"\nPlots:")
print(f"   • logs/plots/01_approval_distribution.png")
print(f"   • logs/plots/02_feature_distributions.png")
print(f"   • logs/plots/03_correlation_matrix.png")
print(f"   • logs/plots/04_confusion_matrix.png")
print(f"   • logs/plots/05_roc_curve.png")
print(f"   • logs/plots/06_feature_importance.png")
print(f"   • logs/plots/07_shap_summary.png")

print(f"\nNext Steps:")
print(f"   1. Review the plots in logs/plots/")
print(f"   2. Train the fraud detection model")
print(f"   3. Build the FastAPI service")
print(f"   4. Integrate with Node.js backend")

print(f"\n{'='*70}")
print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*70}\n")