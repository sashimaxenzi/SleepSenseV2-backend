# test_backend.py
import requests
import json

API_URL = "http://127.0.0.1:8000/predict"

# All stress_level values corrected to integers 0–4
test_cases = [
    {
        "age": 28,
        "gender": "Male",
        "daily_steps": 6000,
        "physical_activity_minutes": 30,
        "screen_time_minutes": 90,
        "sleep_duration": 7.5,
        "stress_level": 0,
        "bmi_category": "Normal"
    },
    {
        "age": 35,
        "gender": "Female",
        "daily_steps": 4200,
        "physical_activity_minutes": 15,
        "screen_time_minutes": 150,
        "sleep_duration": 6.5,
        "stress_level": 2,     # FIXED ← int instead of float
        "bmi_category": "Overweight"
    },
    {
        "age": 40,
        "gender": "Male",
        "daily_steps": 2500,
        "physical_activity_minutes": 5,
        "screen_time_minutes": 220,
        "sleep_duration": 5.5,
        "stress_level": 4,
        "bmi_category": "Obese"
    }
]

print("\n🔍 Running backend tests...\n")

for i, case in enumerate(test_cases, 1):

    print(f"--- Test Case {i} ---")
    print("Input:", case)

    try:
        response = requests.post(API_URL, json=case, timeout=10)
        response.raise_for_status()
        result = response.json()

        print("Prediction:", result.get("prediction"))
        print("Rule-based:", result.get("rule_based"))
        print("ML-based:", result.get("ml_based"))
        print("Confidence:", result.get("confidence"))
        print("Class probabilities:", result.get("class_probabilities"))
        print("\nRecommendations:")
        for rec in result.get("recommendations", []):
            print(" -", rec)

    except Exception as e:
        print("Request failed:", e)

    print("-" * 30)
