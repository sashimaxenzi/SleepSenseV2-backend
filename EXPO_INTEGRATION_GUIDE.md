# Expo App Integration Guide

## Your Backend API URL
```
https://workspace-sashima.replit.dev
```

## Integration Steps for Your Expo Snack App

### Step 1: Add API Configuration

Add this constant at the top of your `App.js` (after imports):

```javascript
const API_URL = "https://workspace-sashima.replit.dev";
```

### Step 2: Create API Call Function

Add this function before your `ManualEntry` component:

```javascript
const getPrediction = async (formData) => {
  try {
    const response = await fetch(`${API_URL}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        age: parseInt(formData.age),
        gender: formData.gender,
        daily_steps: parseFloat(formData.dailySteps) || null,
        physical_activity_minutes: parseFloat(formData.physicalActivity) || null,
        stress_level: parseFloat(formData.stressLevel) || null,
        bmi_category: formData.bmiCategory || null,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to get prediction');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};
```

### Step 3: Modify the `saveData` function

Replace your current `saveData` function with this updated version:

```javascript
const saveData = async () => {
  try {
    // Validate required fields
    if (!form.age || !form.gender) {
      alert("Please fill in at least Age and Gender");
      return;
    }

    // Save to local storage
    await AsyncStorage.setItem("manualEntry", JSON.stringify(form));
    
    // Get prediction from backend
    const prediction = await getPrediction(form);
    
    // Show results
    alert(
      `Sleep Quality Prediction: ${prediction.prediction}\n\n` +
      `Confidence: ${(prediction.confidence * 100).toFixed(1)}%\n\n` +
      `Recommendations:\n${prediction.recommendations.join('\n')}`
    );
    
    // Optionally navigate or save prediction
    navigation.goBack();
  } catch (e) {
    console.log(e);
    alert("Error getting prediction. Please try again.");
  }
};
```

### Step 4: (Optional) Add Loading State

Add a loading state to show when fetching prediction:

```javascript
// Add to your useState declarations
const [loading, setLoading] = useState(false);

// Update saveData to use loading state
const saveData = async () => {
  try {
    if (!form.age || !form.gender) {
      alert("Please fill in at least Age and Gender");
      return;
    }

    setLoading(true);
    
    await AsyncStorage.setItem("manualEntry", JSON.stringify(form));
    const prediction = await getPrediction(form);
    
    setLoading(false);
    
    alert(
      `Sleep Quality Prediction: ${prediction.prediction}\n\n` +
      `Confidence: ${(prediction.confidence * 100).toFixed(1)}%\n\n` +
      `Recommendations:\n${prediction.recommendations.join('\n')}`
    );
    
    navigation.goBack();
  } catch (e) {
    setLoading(false);
    console.log(e);
    alert("Error getting prediction. Please try again.");
  }
};

// Update button to show loading
<TouchableOpacity 
  style={styles.button} 
  onPress={saveData}
  disabled={loading}
>
  <Text style={styles.buttonText}>
    {loading ? "Getting Prediction..." : "Save Entry"}
  </Text>
</TouchableOpacity>
```

## Field Mapping (Your Form → Backend API)

| Your Form Field      | Backend API Field           | Type   |
|---------------------|-----------------------------|--------|
| age                 | age                         | int    |
| gender              | gender                      | string |
| dailySteps          | daily_steps                 | float  |
| physicalActivity    | physical_activity_minutes   | float  |
| stressLevel         | stress_level                | float  |
| bmiCategory         | bmi_category                | string |

**Note:** Fields like `occupation`, `sleepDuration`, `bloodPressure`, etc. are not used by the current prediction model but you can still save them locally for future use.

## API Response Format

```json
{
  "prediction": "Good" or "Poor",
  "confidence": 0.95,
  "recommendations": [
    "High stress detected: try relaxation techniques...",
    "Low daily steps: try a short walk..."
  ],
  "explanation": {
    "note": "Feature importance info",
    "feature_importances": [...]
  }
}
```

## Testing the Integration

1. Fill out the form in your Expo app
2. Click "Save Entry"
3. The app will:
   - Save data locally
   - Send data to backend API
   - Receive prediction
   - Show results in alert

## Next Steps (Optional Enhancements)

1. **Create a Results Screen**: Instead of alert, navigate to a dedicated results screen
2. **Save Prediction History**: Store predictions with timestamps
3. **Better UI**: Display recommendations in a nice card layout
4. **Error Handling**: Add better error messages and retry logic
5. **Add Screen Time**: Add a screen time field to your form (currently missing)

## Quick Test

You can test the API directly in your browser or Postman:

**Endpoint:** `https://workspace-sashima.replit.dev/predict`

**Method:** POST

**Body:**
```json
{
  "age": 28,
  "gender": "Male",
  "daily_steps": 4200,
  "physical_activity_minutes": 42,
  "stress_level": 6,
  "bmi_category": "Normal"
}
```

Happy coding! 🚀
