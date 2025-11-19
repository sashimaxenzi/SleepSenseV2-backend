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
df = pd.read_csv("data/sleep_data.csv")  # data set

# === BASIC CLEANING ===
# Drop rows without sleep_quality
df = df.dropna(subset=["sleep_quality"])

# Binarize target: Good (1) if >=6 else Poor (0)
df['sleep_quality_cat'] = np.where(df['sleep_quality'] >= 6, 1, 0)

# Select features
feature_cols = [
    "age",
    "gender",
    "daily_steps",
    "physical_activity_minutes",
    "screen_time_minutes",
    "stress_level",
    "bmi_category",
    # add other columns as present
]
# Keep rows that have at least one of the feature columns (or handle missing)
df = df[feature_cols + ["sleep_quality_cat"]]

# Split
X = df[feature_cols]
y = df['sleep_quality_cat']

# Identify numeric and categorical columns
numeric_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()

# Preprocessing pipelines
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    # Decision Trees do not require scaling, but scaler is harmless
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

grid = GridSearchCV(pipeline, param_grid=param_grid, cv=5, scoring='f1', n_jobs=-1)
grid.fit(X_train, y_train)

print("Best params:", grid.best_params_)
best_model = grid.best_estimator_

# Evaluate
y_pred = best_model.predict(X_test)
print(classification_report(y_test, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# Save model
joblib.dump(best_model, "models/sleep_quality_decision_tree.pkl")
print("Model saved to models/sleep_quality_decision_tree.pkl")