# train_model.py
import os
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

DATA_PATH = "/Users/sashimaxenzi/Documents/SleepApp/sleep_data.csv"
MODEL_PATH = "models/sleep_quality_decision_tree.pkl"
os.makedirs("models", exist_ok=True)

print("Loading:", DATA_PATH)
df = pd.read_csv(DATA_PATH)
print("Initial columns:", df.columns.tolist())

# rename columns
col_map = {
    "Person ID": "person_id",
    "Gender": "gender",
    "Age": "age",
    "Occupation": "occupation",
    "Sleep Duration": "sleep_duration",
    "Quality of Sleep": "sleep_quality",
    "Physical Activity Level": "physical_activity_minutes",
    "Stress Level": "stress_level_raw",
    "BMI Category": "bmi_category",
    "Blood Pressure": "blood_pressure",
    "Heart Rate": "heart_rate",
    "Daily Steps": "daily_steps",
    "Sleep Disorder": "sleep_disorder"
}
df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

df = df.dropna(subset=["sleep_duration", "physical_activity_minutes", "daily_steps"])

# ---- STRESS LEVEL MAPPING (1–10 → 0–4) ----
def map_stress(x):
    try:
        x = float(x)
        x = min(max(x, 1), 10)
    except:
        return np.nan
    return round((x - 1) * (4 / 9), 2)

df["stress_level"] = df["stress_level_raw"].apply(map_stress)

# ---- RULE-BASED LABEL CREATION (Good / Average / Poor) ----
def rule_sleep_duration(h):
    h = float(h)
    if h < 6 or h >= 9:
        return 1
    elif 6 <= h < 7 or 8 <= h < 9:
        return 2
    else:
        return 3

def rule_daily_steps(s):
    s = float(s)
    if s < 3000:
        return 1
    elif 3000 <= s < 5000:
        return 2
    else:
        return 3

def rule_pa(p):
    p = float(p)
    if p < 10:
        return 1
    elif 10 <= p < 21:
        return 2
    else:
        return 3

def rule_stress(v):
    v = float(v)
    if v >= 3:
        return 1
    elif v == 2:
        return 2
    else:
        return 3

# Build rule scores
df["score_sleep"] = df["sleep_duration"].apply(rule_sleep_duration)
df["score_steps"] = df["daily_steps"].apply(rule_daily_steps)
df["score_pa"] = df["physical_activity_minutes"].apply(rule_pa)
df["score_stress"] = df["stress_level"].apply(rule_stress)

# Only 4-factor scoring (no screen_time in CSV)
df["final_score"] = (df["score_sleep"] + df["score_steps"] + df["score_pa"] + df["score_stress"]) / 4

def map_class(s):
    if s < 1.75:
        return "Poor"
    elif s < 2.4:
        return "Average"
    else:
        return "Good"

df["sleep_quality_bin"] = df["final_score"].apply(map_class)
print("Class distribution:", df["sleep_quality_bin"].value_counts())

# ---- ML FEATURES ----
feature_cols = [
    "age", "gender", "daily_steps", "physical_activity_minutes",
    "sleep_duration", "stress_level", "bmi_category"
]

X = df[feature_cols].copy()
y = df["sleep_quality_bin"].copy()

numeric_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()

numeric_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

categorical_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer([
    ("num", numeric_transformer, numeric_cols),
    ("cat", categorical_transformer, categorical_cols)
])

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("clf", DecisionTreeClassifier(random_state=42, class_weight="balanced"))
])

param_grid = {
    "clf__criterion": ["gini", "entropy"],
    "clf__max_depth": [3, 5, 7, None],
    "clf__min_samples_split": [2, 5, 10]
}

# Train-test split
try:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
except:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

grid = GridSearchCV(pipeline, param_grid, cv=5, scoring="f1_weighted", n_jobs=-1)
grid.fit(X_train, y_train)

best_model = grid.best_estimator_
print("Best params:", grid.best_params_)

y_pred = best_model.predict(X_test)
print("Classification report:\n", classification_report(y_test, y_pred))
print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))

joblib.dump(best_model, MODEL_PATH)
print("Model saved to:", MODEL_PATH)
