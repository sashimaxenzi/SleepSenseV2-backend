# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd


app = FastAPI(title="SleepQuality Recommendation API")


# Add CORS middleware to allow mobile app requests
app.add_middleware(
   CORSMiddleware,
   allow_origins=["*"],  # In production, specify app's domain
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)


# Load model (pipeline includes preprocessing)
model = joblib.load("models/sleep_quality_decision_tree.pkl")


class UserInput(BaseModel):
   age: int
   gender: str
   daily_steps: float = None
   physical_activity_minutes: float = None
   screen_time_minutes: float = None
   stress_level: float = None
   bmi_category: str = None


@app.get("/health")
def health():
   return {"status": "ok"}


@app.post("/predict")
def predict(data: UserInput):
   # Convert input to dataframe
   input_df = pd.DataFrame([data.dict()])


   # Use model pipeline to predict
   pred = model.predict(input_df)[0]
   pred_proba = None
   try:
       proba = model.predict_proba(input_df)[0]
       pred_proba = max(proba)
   except Exception:
       pred_proba = None


   label = "Good" if pred == 1 else "Poor"


   # Feature importances or simple explanation (for DecisionTree pipeline)
   explanation = {}
   try:
       # Attempt to extract feature importances from the tree
       clf = model.named_steps['clf']
       preproc = model.named_steps['preprocessor']
       # Get transformed feature names
       num_cols = preproc.transformers_[0][2]
       cat_cols = preproc.transformers_[1][2]
       # This is approximate; for production create exact feature names list saved during training.
       explanation['note'] = "Top contributing features are available from model.feature_importances_. Exact names require saved feature mapping."
       explanation['feature_importances'] = clf.feature_importances_.tolist()
   except Exception as e:
       explanation['note'] = "Feature importance not available in this deployment: " + str(e)


   # Generate simple rule-based recommendations (mapping)
   recs = []
   #  Rules / Recommendations
   if data.stress_level is not None and data.stress_level >= 7:
       recs.append("High stress detected: try relaxation techniques (10 min mindfulness), avoid screens 1 hr before bed.")
   if data.screen_time_minutes is not None and data.screen_time_minutes >= 90:
       recs.append("High screen time: reduce screen exposure 60 minutes before bedtime.")
   if (data.daily_steps is not None) and (data.daily_steps < 4000):
       recs.append("Low daily steps: try a short walk or light exercise during the day.")
   if not recs:
       recs.append("Maintain your current routines: keep consistent bedtime and healthy lifestyle habits.")


   response = {
       "prediction": label,
       "confidence": float(pred_proba) if pred_proba is not None else None,
       "recommendations": recs,
       "explanation": explanation
   }
   return response
