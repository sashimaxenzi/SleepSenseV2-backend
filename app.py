from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd

# -----------------------------
# FastAPI setup
# -----------------------------
app = FastAPI(title="SleepQuality Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# User Input Model
# -----------------------------
class UserInput(BaseModel):
    age: int
    gender: str
    daily_steps: int
    physical_activity_minutes: int
    sleep_duration: float
    stress_level: int      # user can input 0–10 (we re-map to 0–4)
    bmi_category: str
    screen_time_minutes: int


# -----------------------------
# Load ML model
# -----------------------------
try:
    model = joblib.load("models/sleep_quality_decision_tree.pkl")
except:
    model = None


# -----------------------------
# Recommendations
# -----------------------------
def build_recommendations(data: UserInput):

    recs = []

    # SCREEN TIME
    if data.screen_time_minutes < 120:
        recs.append("Screen time: Good — <2 hours/day. Maintain reduced evening device use and blue-light filters.")
    elif 120 <= data.screen_time_minutes < 180:
        recs.append("Screen time: Average — 2–3 hours/day. Reduce evening screen time and enable blue-light filters.")
    else:
        recs.append("Screen time: Poor — >=3 hours/day. Strongly reduce evening screen exposure; try 1–2 hours no-screen before bed.")

    # SLEEP DURATION
    sd = data.sleep_duration
    if sd < 6 or sd >= 9:
        recs.append("Sleep duration: Poor — <6 or >=9 hours/day linked to higher health risks. Try to target 7–8 hours.")
    elif 6 <= sd < 7 or 8 <= sd < 9:
        recs.append("Sleep duration: Borderline — 6–7 or 8–9 hours. Aim for 7–8 hours when possible.")
    else:
        recs.append("Sleep duration: Good — 7–8 hours/day (optimal). Keep consistent sleep schedule.")

    # DAILY STEPS
    if data.daily_steps < 3000:
        recs.append("Daily steps: Poor — <3000. Start with short walks (10–15 min) and build up.")
    elif 3000 <= data.daily_steps < 5000:
        recs.append("Daily steps: Average — 3000–4999. Add short walks to reach 5000+ steps.")
    else:
        recs.append("Daily steps: Good — >=5000. Maintain daily walking and activity.")

    # PHYSICAL ACTIVITY
    pa = data.physical_activity_minutes
    if pa < 10:
        recs.append("Physical activity: Poor — <10 min/day. Try short frequent sessions and build up.")
    elif 10 <= pa < 21:
        recs.append("Physical activity: Average — 10–20 min/day. Consider increasing to 21+ min.")
    else:
        recs.append("Physical activity: Good — >=21 min/day. Meets recommended weekly moderate activity.")

    # STRESS LEVEL (mapped earlier)
    return recs


# -----------------------------
# PREDICT ENDPOINT
# -----------------------------
@app.post("/predict")
def predict(data: UserInput):

    if model is None:
        return {"error": "Model not loaded"}

    # -----------------------------
    # 1. RULE-BASED SCORING
    # -----------------------------
    score_details = {}

    # Sleep Duration score
    sd = data.sleep_duration
    if sd < 6 or sd >= 9:
        sd_score = 1
    elif 6 <= sd < 7 or 8 <= sd < 9:
        sd_score = 2
    else:
        sd_score = 3
    score_details["sleep_duration"] = sd_score

    # Steps score
    if data.daily_steps < 3000:
        step_score = 1
    elif 3000 <= data.daily_steps < 5000:
        step_score = 2
    else:
        step_score = 3
    score_details["daily_steps"] = step_score

    # Physical Activity score
    pa = data.physical_activity_minutes
    if pa < 10:
        pa_score = 1
    elif 10 <= pa < 21:
        pa_score = 2
    else:
        pa_score = 3
    score_details["physical_activity"] = pa_score

    # Stress (map 0–10 → 0–4)
    s = int((data.stress_level / 10) * 4)
    if s >= 3:
        stress_score = 1
    elif s == 2:
        stress_score = 2
    else:
        stress_score = 3
    score_details["stress"] = stress_score

    # Screen Time
    if data.screen_time_minutes >= 180:
        st_score = 1
    elif 120 <= data.screen_time_minutes < 180:
        st_score = 2
    else:
        st_score = 3
    score_details["screen_time"] = st_score

    # Final RULE-based score (normalize 1–3)
    final_score = (sum(score_details.values()) / (5 * 3)) * 3

    if final_score < 1.5:
        rule_pred = "Poor"
    elif final_score < 2.4:
        rule_pred = "Average"
    else:
        rule_pred = "Good"

    # -----------------------------
    # 2. MACHINE LEARNING PREDICTION
    # -----------------------------
    input_df = pd.DataFrame([data.dict()])
    ml_pred = model.predict(input_df)[0]
    ml_prob = model.predict_proba(input_df)[0]
    confidence = max(ml_prob) * 100

    class_probs = {model.classes_[i]: round(float(ml_prob[i]) * 100, 2)
                   for i in range(len(model.classes_))}

    # -----------------------------
    # 3. RULE OVERRIDE FOR POOR
    # -----------------------------
    if rule_pred == "Poor":
        final_prediction = "Poor"
        final_confidence = 100.0

    # -----------------------------
    # 4. HYBRID: ML CONFIDENCE FALLBACK (<70%)
    # -----------------------------
    elif confidence < 70:
        final_prediction = rule_pred
        final_confidence = 100.0  # rule-based always full confidence

    else:
        final_prediction = ml_pred
        final_confidence = confidence

    # -----------------------------
    # 5. Build recommendations
    # -----------------------------
    recommendations = build_recommendations(data)

    return {
        "prediction": final_prediction,
        "score": final_score,
        "confidence": round(final_confidence, 2),
        "class_probabilities": class_probs,
        "rule_based": rule_pred,
        "ml_based": ml_pred,
        "recommendations": recommendations
    }


@app.get("/")
def root():
    return {"message": "SleepSense API Running"}
