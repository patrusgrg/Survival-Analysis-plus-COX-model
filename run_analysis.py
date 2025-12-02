"""
Comprehensive Survival Analysis with Cox Proportional Hazards Model
Runs all phases: data prep, EDA, Cox modeling, export, and API/UI integration
"""

import os
import sys
import pandas as pd
import numpy as np
import json
import joblib
from pathlib import Path
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.statistics import logrank_test, proportional_hazard_test
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*80)
print("🏥 SURVIVAL ANALYSIS + COX PROPORTIONAL HAZARDS MODEL")
print("="*80)

# ============================================================================
# PHASE 1: Load and Explore Dataset
# ============================================================================
print("\n📋 PHASE 1: Loading and Exploring Dataset...")

# Ensure data directory exists
Path('data').mkdir(exist_ok=True)
Path('models').mkdir(exist_ok=True)
Path('figures').mkdir(exist_ok=True)

# Load dataset
csv_path = Path('data/heart.csv')
if not csv_path.exists():
    csv_path = Path('heart.csv')
    if not csv_path.exists():
        raise FileNotFoundError(f"❌ heart.csv not found in {Path.cwd()}")

df = pd.read_csv(csv_path)
print(f"✅ Dataset loaded: {df.shape[0]} samples, {df.shape[1]} features")
print(f"\n📊 Dataset Overview:")
print(df.head())
print(f"\n📈 Statistical Summary:")
print(df.describe())

# ============================================================================
# PHASE 2: Data Cleaning & Preprocessing
# ============================================================================
print("\n📋 PHASE 2: Data Cleaning & Preprocessing...")

# Check for missing values
missing = df.isnull().sum()
if missing.sum() == 0:
    print("✅ No missing values detected")
else:
    print(f"⚠️  Missing values found:\n{missing[missing > 0]}")
    df = df.dropna()

# Create copy for preprocessing
df_clean = df.copy()

# Rename columns for clarity
column_mapping = {
    'Age': 'time',
    'HeartDisease': 'event',
    'Sex': 'sex',
    'ChestPainType': 'chest_pain_type',
    'RestingBP': 'resting_bp',
    'Cholesterol': 'cholesterol',
    'FastingBS': 'fasting_bs',
    'RestingECG': 'resting_ecg',
    'MaxHR': 'max_hr',
    'ExerciseAngina': 'exercise_angina',
    'Oldpeak': 'oldpeak',
    'ST_Slope': 'st_slope'
}

df_clean.rename(columns=column_mapping, inplace=True)
print(f"✅ Columns renamed")

# Handle zero cholesterol values (data quality issue)
if (df_clean['cholesterol'] == 0).any():
    median_chol = df_clean[df_clean['cholesterol'] > 0]['cholesterol'].median()
    df_clean['cholesterol'].replace(0, median_chol, inplace=True)
    print(f"✅ Zero cholesterol values replaced with median ({median_chol:.0f})")

print(f"\n📊 Cleaned Dataset Shape: {df_clean.shape}")
print(f"💾 Event Rate: {(df_clean['event'].sum() / len(df_clean) * 100):.1f}%")

# ============================================================================
# PHASE 3: Train-Test Split & Preprocessing Pipeline
# ============================================================================
print("\n📋 PHASE 3: Train-Test Split & Preprocessing Pipeline...")

# Separate features and target
X = df_clean.drop(columns=['time', 'event'])
y_time = df_clean['time']
y_event = df_clean['event']

# Train-test split (stratified by event)
X_train, X_test, y_time_train, y_time_test, y_event_train, y_event_test = \
    train_test_split(X, y_time, y_event, test_size=0.2, random_state=42, stratify=y_event)

print(f"✅ Train set: {len(X_train)} samples (event rate: {(y_event_train.sum() / len(X_train) * 100):.1f}%)")
print(f"✅ Test set: {len(X_test)} samples (event rate: {(y_event_test.sum() / len(X_test) * 100):.1f}%)")

# Identify categorical and numerical columns
categorical_cols = X_train.select_dtypes(include=['object']).columns.tolist()
numerical_cols = X_train.select_dtypes(include=['int64', 'float64']).columns.tolist()

print(f"📊 Categorical features: {categorical_cols}")
print(f"📊 Numerical features: {numerical_cols}")

# Encode categorical variables
label_encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    X_train[col] = le.fit_transform(X_train[col].astype(str))
    X_test[col] = le.transform(X_test[col].astype(str))
    label_encoders[col] = le
    print(f"✅ Encoded {col}: {dict(enumerate(le.classes_))}")

# Scale numerical features
scaler = StandardScaler()
X_train[numerical_cols] = scaler.fit_transform(X_train[numerical_cols])
X_test[numerical_cols] = scaler.transform(X_test[numerical_cols])
print(f"✅ Scaled {len(numerical_cols)} numerical features")

# Create train/test DataFrames
train_df = X_train.copy()
train_df['time'] = y_time_train.values
train_df['event'] = y_event_train.values

test_df = X_test.copy()
test_df['time'] = y_time_test.values
test_df['event'] = y_event_test.values

# Save train/test splits
train_df.to_csv('data/train.csv', index=False)
test_df.to_csv('data/test.csv', index=False)
print(f"✅ Train/test sets saved to data/ directory")

# ============================================================================
# PHASE 4: Kaplan-Meier Survival Analysis
# ============================================================================
print("\n📋 PHASE 4: Kaplan-Meier Survival Analysis...")

kmf = KaplanMeierFitter()
kmf.fit(train_df['time'], train_df['event'], label='Overall Survival')

print(f"✅ Kaplan-Meier estimator fitted")
print(f"📊 Median survival age: {kmf.median_survival_time_:.1f} years")

# Create Kaplan-Meier plot
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
kmf.plot_survival_function(ci_show=True)
plt.title('Overall Survival Curve (Kaplan-Meier)', fontsize=12, fontweight='bold')
plt.xlabel('Age (years)')
plt.ylabel('Survival Probability')
plt.grid(alpha=0.3)

# Stratified analysis by sex
plt.subplot(1, 2, 2)
for sex in train_df['sex'].unique():
    mask = train_df['sex'] == sex
    kmf_strat = KaplanMeierFitter()
    kmf_strat.fit(train_df.loc[mask, 'time'], train_df.loc[mask, 'event'], 
                   label=f'Sex={sex}')
    kmf_strat.plot_survival_function(ci_show=False)

plt.title('Stratified Survival Curves (by Sex)', fontsize=12, fontweight='bold')
plt.xlabel('Age (years)')
plt.ylabel('Survival Probability')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('figures/01_kaplan_meier_curves.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"✅ Kaplan-Meier curves saved to figures/01_kaplan_meier_curves.png")

# Log-rank test
results = logrank_test(
    train_df[train_df['sex'] == 0]['time'],
    train_df[train_df['sex'] == 1]['time'],
    train_df[train_df['sex'] == 0]['event'],
    train_df[train_df['sex'] == 1]['event']
)
print(f"📊 Log-rank test (Sex difference): p-value = {results.p_value:.6f}")
if results.p_value < 0.05:
    print(f"✅ Significant difference in survival by sex (p < 0.05)")
else:
    print(f"⚠️  No significant difference in survival by sex (p >= 0.05)")

# ============================================================================
# PHASE 5: Cox Proportional Hazards Model
# ============================================================================
print("\n📋 PHASE 5: Cox Proportional Hazards Model...")

cph = CoxPHFitter()
cph.fit(train_df, duration_col='time', event_col='event')

print(f"✅ Cox model fitted successfully")
print(f"\n📊 Model Summary:")
print(cph.summary)

# Get concordance index
c_index = cph.concordance_index_
print(f"\n📈 Concordance Index (C-Index): {c_index:.4f}")
if c_index > 0.7:
    print(f"✅ Excellent discrimination (C-Index > 0.7)")
elif c_index > 0.6:
    print(f"✅ Good discrimination (C-Index > 0.6)")
else:
    print(f"⚠️  Fair discrimination (C-Index <= 0.6)")

# Plot hazard ratios
plt.figure(figsize=(10, 8))
cph.plot(ax=plt.gca())
plt.title('Cox Model: Hazard Ratios with 95% CI', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('figures/02_hazard_ratios.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"✅ Hazard ratios plot saved to figures/02_hazard_ratios.png")

# Check proportional hazards assumption
print(f"\n🔍 Proportional Hazards Assumption Test:")
ph_test = proportional_hazard_test(cph, train_df, time_transform='rank')
print(ph_test)

# ============================================================================
# PHASE 6: Model Evaluation & Predictions
# ============================================================================
print("\n📋 PHASE 6: Model Evaluation & Predictions...")

# Test set evaluation
from lifelines.utils import concordance_index
test_concordance = concordance_index(test_df['time'], -cph.predict_partial_hazard(test_df.drop(columns=['time', 'event'])), test_df['event'])
print(f"📊 Test Set Concordance Index: {test_concordance:.4f}")

# Sample predictions
sample_patient = test_df.iloc[0]
partial_hazard = cph.predict_partial_hazard(pd.DataFrame([sample_patient.drop(['time', 'event'])]))
survival_func = cph.predict_survival_function(pd.DataFrame([sample_patient.drop(['time', 'event'])]))

print(f"\n📋 Sample Patient Prediction:")
print(f"  Partial Hazard: {partial_hazard.values[0]:.4f}")
print(f"  Median Survival: {survival_func.index[survival_func.values[:, 0] <= 0.5][0] if (survival_func.values[:, 0] <= 0.5).any() else 'N/A'}")

# ============================================================================
# PHASE 7: Export Model & Artifacts
# ============================================================================
print("\n📋 PHASE 7: Exporting Model & Artifacts...")

# Save Cox model
joblib.dump(cph, 'models/cox_model.pkl')
print(f"✅ Cox model saved to models/cox_model.pkl")

# Save preprocessing artifacts
preprocessing_artifacts = {
    'label_encoders': label_encoders,
    'scaler': scaler,
    'numerical_cols': numerical_cols,
    'categorical_cols': categorical_cols,
    'feature_names': X_train.columns.tolist(),
    'c_index': float(c_index),
    'test_c_index': float(test_concordance)
}

joblib.dump(preprocessing_artifacts, 'models/preprocessing_artifacts.pkl')
print(f"✅ Preprocessing artifacts saved to models/preprocessing_artifacts.pkl")

# Save model summary
with open('models/model_summary.txt', 'w') as f:
    f.write("="*80 + "\n")
    f.write("SURVIVAL ANALYSIS + COX PROPORTIONAL HAZARDS MODEL\n")
    f.write("="*80 + "\n\n")
    f.write(f"Dataset: heart.csv\n")
    f.write(f"Training samples: {len(train_df)}\n")
    f.write(f"Test samples: {len(test_df)}\n")
    f.write(f"Event rate: {(train_df['event'].sum() / len(train_df) * 100):.1f}%\n\n")
    f.write(f"Model: Cox Proportional Hazards\n")
    f.write(f"Concordance Index (Train): {c_index:.4f}\n")
    f.write(f"Concordance Index (Test): {test_concordance:.4f}\n\n")
    f.write("Feature Names:\n")
    for i, feat in enumerate(X_train.columns.tolist(), 1):
        f.write(f"  {i}. {feat}\n")
    f.write("\n" + str(cph.summary) + "\n")

print(f"✅ Model summary saved to models/model_summary.txt")

# ============================================================================
# SUMMARY & NEXT STEPS
# ============================================================================
print("\n" + "="*80)
print("✅ ANALYSIS COMPLETE!")
print("="*80)
print(f"\n📁 Generated Files:")
print(f"  ✓ data/train.csv - Training dataset ({len(train_df)} samples)")
print(f"  ✓ data/test.csv - Test dataset ({len(test_df)} samples)")
print(f"  ✓ models/cox_model.pkl - Trained Cox model")
print(f"  ✓ models/preprocessing_artifacts.pkl - Encoder & scaler objects")
print(f"  ✓ models/model_summary.txt - Model metrics & features")
print(f"  ✓ figures/01_kaplan_meier_curves.png - Survival curves")
print(f"  ✓ figures/02_hazard_ratios.png - Hazard ratio plot")

print(f"\n🚀 Next Steps:")
print(f"  1. Backend API: cd backend && uvicorn main:app --reload")
print(f"  2. Frontend UI: cd frontend && streamlit run app.py")
print(f"  3. Or Docker: docker-compose up -d")
print(f"\n📊 Model Performance:")
print(f"  • Training C-Index: {c_index:.4f}")
print(f"  • Test C-Index: {test_concordance:.4f}")
print(f"  • Features: {len(X_train.columns)}")
print(f"  • Samples: {len(df_clean)}")

print("\n✨ All systems ready for API and UI deployment!")
print("="*80 + "\n")
