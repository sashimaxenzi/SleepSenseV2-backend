# train_model.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# === LOAD DATA ===
df = pd.read_csv("data/sleep_data.csv")

# === BASIC CLEANING ===
# Drop rows without Quality of Sleep
df = df.dropna(subset=["Quality of Sleep"])

# Binarize target: Good (1) if >=6 else Poor (0)
df['sleep_quality_cat'] = np.where(df['Quality of Sleep'] >= 6, 1, 0)

# Select features based on the actual CSV columns
feature_cols = [
    "Age",
    "Gender",
    "Daily Steps",
    "Physical Activity Level",
    "Stress Level",
    "BMI Category",
]

# Keep only relevant columns
df_clean = df[feature_cols + ["sleep_quality_cat"]].copy()

# Rename columns to match API expected names (lowercase with underscores)
df_clean.columns = [
    "age",
    "gender",
    "daily_steps",
    "physical_activity_minutes",
    "stress_level",
    "bmi_category",
    "sleep_quality_cat"
]

# Split
X = df_clean.drop("sleep_quality_cat", axis=1)
y = df_clean['sleep_quality_cat']

# Identify numeric and categorical columns
numeric_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()

print(f"Numeric columns: {numeric_cols}")
print(f"Categorical columns: {categorical_cols}")

# Preprocessing pipelines
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(transformers=[
    ('num', numeric_transformer, numeric_cols),
    ('cat', categorical_transformer, categorical_cols)
])

# Full pipeline with classifier
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('clf', DecisionTreeClassifier(random_state=42))
])

# Hyperparameter tuning (grid)
param_grid = {
    'clf__criterion': ['gini', 'entropy'],
    'clf__max_depth': [3, 5, 7, 9, None],
    'clf__min_samples_split': [2, 5, 10]
}

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, stratify=y, random_state=42)

print(f"\nTraining model with {len(X_train)} samples...")
grid = GridSearchCV(pipeline, param_grid=param_grid, cv=5, scoring='f1', n_jobs=-1)
grid.fit(X_train, y_train)

print("Best params:", grid.best_params_)
best_model = grid.best_estimator_

# Evaluate
y_pred = best_model.predict(X_test)
print("\n=== Model Performance ===")
print(classification_report(y_test, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# Save model
import os
os.makedirs("models", exist_ok=True)
joblib.dump(best_model, "models/sleep_quality_decision_tree.pkl")
print("\n✅ Model saved to models/sleep_quality_decision_tree.pkl")
