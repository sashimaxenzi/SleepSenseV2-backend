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
    stress_level: int      # user provides 0–4 from the UI
    bmi_category: str
    screen_time_minutes: int

# -----------------------------
# Load ML Model
# -----------------------------
try:
    model = joblib.load("models/sleep_quality_decision_tree.pkl")
except:
    model = None

# -----------------------------
# Recommendations (Rewritten clearly)
# -----------------------------
def build_recommendations(data: UserInput):

    recs = []

    # SCREEN TIME
    if data.screen_time_minutes < 120:
        recs.append(
            "Your screen time is within a healthy range. Try to continue keeping device use low in the evening."
        )
    elif 120 <= data.screen_time_minutes < 180:
        recs.append(
            "Your screen time is moderate. Reducing device use before bedtime can improve your sleep quality."
        )
    else:
        recs.append(
            "Your screen time is higher than recommended. Limiting screens 1–2 hours before bed can help you sleep better."
        )

    # SLEEP DURATION
    sd = data.sleep_duration
    if sd < 6 or sd >= 9:
        recs.append(
            "Your sleep duration is outside the recommended range. Aim for 7 to 8 hours of sleep each night."
        )
    elif 6 <= sd < 7 or 8 <= sd < 9:
        recs.append(
            "Your sleep duration is close to ideal but could be improved. Try maintaining a consistent bedtime schedule."
        )
    else:
        recs.append(
            "Your sleep duration looks good. Continue maintaining consistent sleep habits."
        )

    # DAILY STEPS
    if data.daily_steps < 3000:
        recs.append(
            "Your daily activity is low. Adding short walks throughout the day can boost sleep quality."
        )
    elif 3000 <= data.daily_steps < 5000:
        recs.append(
            "Your activity level is moderate. Increasing your steps to at least 5000 per day can be beneficial."
        )
    else:
        recs.append(
            "Your activity level is healthy. Keep up the good movement habits."
        )

    # PHYSICAL ACTIVITY
    pa = data.physical_activity_minutes
    if pa < 10:
        recs.append(
            "Your physical activity is low. Try to include short exercise sessions throughout the week."
        )
    elif 10 <= pa < 21:
        recs.append(
            "You’re getting some activity. Increasing to at least 20 minutes per day may help improve sleep."
        )
    else:
        recs.append(
            "Your physical activity level is great. Staying active supports healthy sleep patterns."
        )

    return recs


# -----------------------------
# Prediction Endpoint
# -----------------------------
@app.post("/predict")
def predict(data: UserInput):

    if model is None:
        return {"error": "Model not loaded"}

    # -----------------------------
    # RULE-BASED SCORING
    # -----------------------------
    score_details = {}

    # Sleep Duration
    sd = data.sleep_duration
    if sd < 6 or sd >= 9:
        sd_score = 1
    elif 6 <= sd < 7 or 8 <= sd < 9:
        sd_score = 2
    else:
        sd_score = 3
    score_details["sleep_duration"] = sd_score

    # Daily Steps
    if data.daily_steps < 3000:
        step_score = 1
    elif 3000 <= data.daily_steps < 5000:
        step_score = 2
    else:
        step_score = 3
    score_details["daily_steps"] = step_score

    # Physical Activity
    pa = data.physical_activity_minutes
    if pa < 10:
        pa_score = 1
    elif 10 <= pa < 21:
        pa_score = 2
    else:
        pa_score = 3
    score_details["physical_activity"] = pa_score

    # Stress (0–4 directly)
    if data.stress_level >= 3:
        stress_score = 1
    elif data.stress_level == 2:
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

    # Final RULE-based score
    final_score = (sum(score_details.values()) / (5 * 3)) * 3

    if final_score < 1.5:
        rule_pred = "Poor"
    elif final_score < 2.4:
        rule_pred = "Average"
    else:
        rule_pred = "Good"

    # -----------------------------
    # MACHINE LEARNING PREDICTION
    # -----------------------------
    input_df = pd.DataFrame([data.dict()])
    ml_pred = model.predict(input_df)[0]
    ml_prob = model.predict_proba(input_df)[0]
    confidence = max(ml_prob) * 100

    class_probs = {
        model.classes_[i]: round(float(ml_prob[i]) * 100, 2)
        for i in range(len(model.classes_))
    }

    # -----------------------------
    # RULE OVERRIDE (Poor always wins)
    # -----------------------------
    if rule_pred == "Poor":
        final_prediction = "Poor"
        final_confidence = 100.0

    # -----------------------------
    # ML fallback if low confidence
    # -----------------------------
    elif confidence < 70:
        final_prediction = rule_pred
        final_confidence = 100.0
    else:
        final_prediction = ml_pred
        final_confidence = confidence

    # -----------------------------
    # Build recommendations
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
