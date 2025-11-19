import React, { useState } from "react";
import { View, Text, TextInput, ScrollView, StyleSheet, TouchableOpacity, Platform } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";

// ⚠️ REPLACE THIS WITH YOUR ACTUAL URL FROM REPLIT WEBVIEW
const API_URL = "https://workspace-sashima.replit.dev";

// Function to get prediction from backend
const getPrediction = async (formData) => {
  try {
    console.log("Sending request to:", `${API_URL}/predict`);
    console.log("Request data:", {
      age: parseInt(formData.age),
      gender: formData.gender,
      daily_steps: parseFloat(formData.dailySteps) || null,
      physical_activity_minutes: parseFloat(formData.physicalActivity) || null,
      stress_level: parseFloat(formData.stressLevel) || null,
      bmi_category: formData.bmiCategory || null,
    });

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

    console.log("Response status:", response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.log("Error response:", errorText);
      throw new Error(`Server error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    console.log("Success! Response:", data);
    return data;
  } catch (error) {
    console.error('API Error Details:', error);
    console.error('Error message:', error.message);
    throw error;
  }
};

// Simple picker button component
const PickerButton = ({ label, value, options, onSelect }) => {
  const [showOptions, setShowOptions] = useState(false);

  return (
    <View>
      <TouchableOpacity 
        style={styles.pickerButton}
        onPress={() => setShowOptions(!showOptions)}
      >
        <Text style={value ? styles.pickerButtonTextSelected : styles.pickerButtonText}>
          {value || label}
        </Text>
        <Text style={styles.pickerArrow}>▼</Text>
      </TouchableOpacity>
      
      {showOptions && (
        <View style={styles.optionsContainer}>
          {options.map((option) => (
            <TouchableOpacity
              key={option.value}
              style={styles.option}
              onPress={() => {
                onSelect(option.value);
                setShowOptions(false);
              }}
            >
              <Text style={styles.optionText}>{option.label}</Text>
            </TouchableOpacity>
          ))}
        </View>
      )}
    </View>
  );
};

export default function ManualEntry({ navigation }) {
  const [form, setForm] = useState({
    gender: "",
    age: "",
    occupation: "",
    sleepDuration: "",
    sleepQuality: "",
    physicalActivity: "",
    stressLevel: "",
    bmiCategory: "",
    bloodPressure: "",
    heartRate: "",
    dailySteps: "",
    sleepDisorder: "",
  });

  const [loading, setLoading] = useState(false);

  const handleChange = (key, value) => {
    setForm({ ...form, [key]: value });
  };

  const saveData = async () => {
    try {
      // Validate required fields
      if (!form.age || !form.gender) {
        alert("Please fill in at least Age and Gender");
        return;
      }

      setLoading(true);

      // Save to local storage
      await AsyncStorage.setItem("manualEntry", JSON.stringify(form));
      
      // Get prediction from backend
      console.log("Fetching prediction...");
      const prediction = await getPrediction(form);
      
      setLoading(false);
      
      // Show results
      alert(
        `✅ Sleep Quality Prediction: ${prediction.prediction}\n\n` +
        `📊 Confidence: ${(prediction.confidence * 100).toFixed(1)}%\n\n` +
        `💡 Recommendations:\n• ${prediction.recommendations.join('\n• ')}`
      );
      
      navigation.goBack();
    } catch (e) {
      setLoading(false);
      console.log("Full error:", e);
      
      // More detailed error message
      let errorMessage = "Error getting prediction.\n\n";
      if (e.message.includes("Network request failed")) {
        errorMessage += "Network error: Cannot reach the server.\n\n" +
          "Solutions:\n" +
          "1. Check if the Replit server is running\n" +
          "2. Make sure the API_URL is correct\n" +
          "3. Try updating the URL in the code";
      } else if (e.message.includes("Server error")) {
        errorMessage += e.message;
      } else {
        errorMessage += `Details: ${e.message}`;
      }
      
      alert(errorMessage);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.header}>Sleep & Lifestyle Entry</Text>
      
      <View style={styles.urlInfo}>
        <Text style={styles.urlText}>API: {API_URL}</Text>
      </View>

      {/* Gender */}
      <Text style={styles.label}>Gender</Text>
      <PickerButton
        label="Select Gender"
        value={form.gender}
        options={[
          { label: "Male", value: "Male" },
          { label: "Female", value: "Female" },
        ]}
        onSelect={(v) => handleChange("gender", v)}
      />

      {/* Age */}
      <Text style={styles.label}>Age</Text>
      <TextInput
        style={styles.input}
        keyboardType="numeric"
        placeholder="Enter age"
        value={form.age}
        onChangeText={(v) => handleChange("age", v)}
      />

      {/* Occupation */}
      <Text style={styles.label}>Occupation</Text>
      <TextInput
        style={styles.input}
        placeholder="e.g., Engineer, Student"
        value={form.occupation}
        onChangeText={(v) => handleChange("occupation", v)}
      />

      {/* Sleep Duration */}
      <Text style={styles.label}>Sleep Duration (hours)</Text>
      <TextInput
        style={styles.input}
        keyboardType="numeric"
        placeholder="e.g., 7.5"
        value={form.sleepDuration}
        onChangeText={(v) => handleChange("sleepDuration", v)}
      />

      {/* Sleep Quality */}
      <Text style={styles.label}>Quality of Sleep (1-10)</Text>
      <TextInput
        style={styles.input}
        keyboardType="numeric"
        placeholder="Rate sleep quality"
        value={form.sleepQuality}
        onChangeText={(v) => handleChange("sleepQuality", v)}
      />

      {/* Physical Activity */}
      <Text style={styles.label}>Physical Activity (minutes/day)</Text>
      <TextInput
        style={styles.input}
        keyboardType="numeric"
        placeholder="e.g., 30"
        value={form.physicalActivity}
        onChangeText={(v) => handleChange("physicalActivity", v)}
      />

      {/* Stress Level */}
      <Text style={styles.label}>Stress Level (1-10)</Text>
      <TextInput
        style={styles.input}
        keyboardType="numeric"
        placeholder="Rate stress level"
        value={form.stressLevel}
        onChangeText={(v) => handleChange("stressLevel", v)}
      />

      {/* BMI Category */}
      <Text style={styles.label}>BMI Category</Text>
      <PickerButton
        label="Select Category"
        value={form.bmiCategory}
        options={[
          { label: "Underweight", value: "Underweight" },
          { label: "Normal", value: "Normal" },
          { label: "Overweight", value: "Overweight" },
          { label: "Obese", value: "Obese" },
        ]}
        onSelect={(v) => handleChange("bmiCategory", v)}
      />

      {/* Blood Pressure */}
      <Text style={styles.label}>Blood Pressure (systolic/diastolic)</Text>
      <TextInput
        style={styles.input}
        placeholder="e.g., 120/80"
        value={form.bloodPressure}
        onChangeText={(v) => handleChange("bloodPressure", v)}
      />

      {/* Heart Rate */}
      <Text style={styles.label}>Heart Rate (bpm)</Text>
      <TextInput
        style={styles.input}
        keyboardType="numeric"
        placeholder="e.g., 70"
        value={form.heartRate}
        onChangeText={(v) => handleChange("heartRate", v)}
      />

      {/* Daily Steps */}
      <Text style={styles.label}>Daily Steps</Text>
      <TextInput
        style={styles.input}
        keyboardType="numeric"
        placeholder="e.g., 5000"
        value={form.dailySteps}
        onChangeText={(v) => handleChange("dailySteps", v)}
      />

      {/* Sleep Disorder */}
      <Text style={styles.label}>Sleep Disorder</Text>
      <PickerButton
        label="Select Option"
        value={form.sleepDisorder}
        options={[
          { label: "None", value: "None" },
          { label: "Insomnia", value: "Insomnia" },
          { label: "Sleep Apnea", value: "Sleep Apnea" },
        ]}
        onSelect={(v) => handleChange("sleepDisorder", v)}
      />

      <TouchableOpacity 
        style={[styles.button, loading && styles.buttonDisabled]} 
        onPress={saveData}
        disabled={loading}
      >
        <Text style={styles.buttonText}>
          {loading ? "Getting Prediction..." : "Save Entry"}
        </Text>
      </TouchableOpacity>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

// ---------- Styles ----------
const styles = StyleSheet.create({
  container: {
    padding: 20,
    backgroundColor: "#fff",
  },
  header: {
    fontSize: 24,
    fontWeight: "700",
    marginBottom: 10,
  },
  urlInfo: {
    backgroundColor: "#f0f0f0",
    padding: 10,
    borderRadius: 5,
    marginBottom: 20,
  },
  urlText: {
    fontSize: 10,
    color: "#666",
  },
  label: {
    fontSize: 16,
    marginTop: 15,
  },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    padding: 12,
    borderRadius: 8,
    marginTop: 5,
  },
  pickerButton: {
    borderWidth: 1,
    borderColor: "#ccc",
    backgroundColor: "#f9f9f9",
    padding: 12,
    borderRadius: 8,
    marginTop: 5,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  pickerButtonText: {
    color: "#999",
  },
  pickerButtonTextSelected: {
    color: "#000",
  },
  pickerArrow: {
    fontSize: 12,
    color: "#666",
  },
  optionsContainer: {
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 8,
    marginTop: 5,
    backgroundColor: "#fff",
  },
  option: {
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
  },
  optionText: {
    fontSize: 16,
  },
  button: {
    backgroundColor: "#4b7bec",
    padding: 15,
    borderRadius: 10,
    marginTop: 30,
    alignItems: "center",
  },
  buttonDisabled: {
    backgroundColor: "#a0b8e8",
  },
  buttonText: {
    color: "white",
    fontSize: 18,
    fontWeight: "600",
  },
});
