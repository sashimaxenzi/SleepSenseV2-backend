# app.py
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
import io

app = FastAPI(title="SleepQuality Recommendation API")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load model (pipeline includes preprocessing)
import os
model = None
model_path = "models/sleep_quality_decision_tree.pkl"
if os.path.exists(model_path):
    model = joblib.load(model_path)
else:
    print(f"Warning: Model not found at {model_path}. Please train the model first using train_model.py")

class UserInput(BaseModel):
    age: int
    gender: str
    daily_steps: float = None
    physical_activity_minutes: float = None
    screen_time_minutes: float = None
    stress_level: float = None
    bmi_category: str = None
    # add other optional fields if in your dataset

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", "r") as f:
        return f.read()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(data: UserInput):
    if model is None:
        return JSONResponse(
            status_code=503,
            content={"error": "Model not loaded. Please train the model first using train_model.py"}
        )
    
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
    # Example rules (these are suggestions; tune to your tree's findings)
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

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file with columns matching the UserInput model.
    Returns predictions for all rows in the CSV.
    """
    if model is None:
        return JSONResponse(
            status_code=503,
            content={"error": "Model not loaded. Please train the model first using train_model.py"}
        )
    
    try:
        # Read the uploaded file
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # Make predictions for all rows
        predictions = model.predict(df)
        
        # Try to get probabilities
        try:
            probabilities = model.predict_proba(df)
            confidences = [max(proba) for proba in probabilities]
        except Exception:
            confidences = [None] * len(predictions)
        
        # Create results
        results = []
        for idx, (pred, conf) in enumerate(zip(predictions, confidences)):
            label = "Good" if pred == 1 else "Poor"
            
            # Generate recommendations for each row
            recs = []
            row = df.iloc[idx]
            
            if 'stress_level' in df.columns and pd.notna(row['stress_level']) and row['stress_level'] >= 7:
                recs.append("High stress detected: try relaxation techniques (10 min mindfulness), avoid screens 1 hr before bed.")
            if 'screen_time_minutes' in df.columns and pd.notna(row['screen_time_minutes']) and row['screen_time_minutes'] >= 90:
                recs.append("High screen time: reduce screen exposure 60 minutes before bedtime.")
            if 'daily_steps' in df.columns and pd.notna(row['daily_steps']) and row['daily_steps'] < 4000:
                recs.append("Low daily steps: try a short walk or light exercise during the day.")
            if not recs:
                recs.append("Maintain your current routines: keep consistent bedtime and healthy lifestyle habits.")
            
            results.append({
                "row": idx + 1,
                "prediction": label,
                "confidence": float(conf) if conf is not None else None,
                "recommendations": recs
            })
        
        return {
            "total_rows": len(results),
            "predictions": results
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": f"Failed to process CSV: {str(e)}"}
        )