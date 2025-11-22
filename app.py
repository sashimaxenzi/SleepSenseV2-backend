from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI()

# -----------------------------
# Input Model
# -----------------------------
class UserInput(BaseModel):
    age: int | None
    gender: str | None
    daily_steps: float | None
    physical_activity_minutes: float | None
    sleep_duration: float | None
    stress_level: int | None
    bmi_category: str | None
    screen_time_minutes: float | None


# -----------------------------
# Load model
# -----------------------------
model = joblib.load("sleep_quality_model.pkl")

# For confidence scoring
def softmax(x):
    e = np.exp(x - np.max(x))
    return e / e.sum()


# -----------------------------
# Clean, Friendly Recommendations
# -----------------------------
def build_recommendations(data: UserInput):
    recs = []

    # SCREEN TIME
    st = data.screen_time_minutes
    if st < 120:
        recs.append("Your screen time looks healthy. Keep it under 2 hours a day and continue limiting screen use before bedtime.")
    elif 120 <= st < 180:
        recs.append("Your screen time is moderate. Try reducing evening screen exposure to help improve sleep quality.")
    else:
        recs.append("You spend quite a lot of time on screens. Try to limit screens in the evening and aim for at least 1–2 hours of screen-free time before bed.")

    # SLEEP DURATION
    sd = data.sleep_duration
    if sd < 6 or sd >= 9:
        recs.append("Your sleep duration is outside the optimal range. Try aiming for 7–8 hours of sleep each night.")
    elif 6 <= sd < 7 or 8 <= sd < 9:
        recs.append("Your sleep duration is close to ideal. Try adjusting your routine to consistently reach 7–8 hours.")
    else:
        recs.append("Your sleep duration is in a great range. Keep maintaining a consistent sleep schedule.")

    # DAILY STEPS
    steps = data.daily_steps
    if steps < 3000:
        recs.append("You're getting fewer steps than recommended. Consider adding short walks during the day to gradually increase activity.")
    elif 3000 <= steps < 5000:
        recs.append("Your activity level is moderate. A few extra short walks can help you reach a healthier step count.")
    else:
        recs.append("Great job staying active! Keep maintaining your current level of daily movement.")

    # PHYSICAL ACTIVITY
    pa = data.physical_activity_minutes
    if pa < 10:
        recs.append("You’re doing very little physical activity. Try adding short, light routines to slowly build a healthy habit.")
    elif 10 <= pa < 21:
        recs.append("Your activity level is okay. Adding just a bit more daily movement can bring you into the recommended range.")
    else:
        recs.append("You're meeting the recommended activity levels. Keep up the good work!")

    return recs


# -----------------------------
# Prediction Route
# -----------------------------
@app.post("/predict")
def predict_sleep_quality(data: UserInput):

    # Handle missing values safely
    X = np.array([[
        data.age or 0,
        1 if (data.gender and data.gender.lower() == "male") else 0,
        data.daily_steps or 0,
        data.physical_activity_minutes or 0,
        data.sleep_duration or 0,
        data.stress_level or 0,
        {"Underweight": 0, "Normal": 1, "Overweight": 2, "Obese": 3}.get(data.bmi_category, 1),
        data.screen_time_minutes or 0
    ]])

    # Predict label
    pred_idx = model.predict(X)[0]
    pred_label = ["Poor", "Average", "Good"][pred_idx]

    # Confidence
    proba = softmax(model.predict_proba(X)[0])
    confidence = round(float(proba[pred_idx] * 100), 2)

    return {
        "prediction": pred_label,
        "confidence": confidence,
        "recommendations": build_recommendations(data)
    }


@app.get("/")
def root():
    return {"message": "SleepSense backend running"}
