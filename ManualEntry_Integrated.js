import React, { useState } from "react";
import { View, Text, TextInput, ScrollView, StyleSheet, TouchableOpacity } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Picker } from "@react-native-picker/picker";

// Backend API URL
const API_URL = "https://workspace-sashima.replit.dev";

// Function to get prediction from backend
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
      const prediction = await getPrediction(form);
      
      setLoading(false);
      
      // Show results
      alert(
        `Sleep Quality Prediction: ${prediction.prediction}\n\n` +
        `Confidence: ${(prediction.confidence * 100).toFixed(1)}%\n\n` +
        `Recommendations:\n• ${prediction.recommendations.join('\n• ')}`
      );
      
      navigation.goBack();
    } catch (e) {
      setLoading(false);
      console.log(e);
      alert("Error getting prediction. Please check your internet connection and try again.");
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.header}>Sleep & Lifestyle Entry</Text>

      {/* Gender */}
      <Text style={styles.label}>Gender</Text>
      <Picker
        selectedValue={form.gender}
        onValueChange={(v) => handleChange("gender", v)}
        style={styles.picker}
      >
        <Picker.Item label="Select Gender" value="" />
        <Picker.Item label="Male" value="Male" />
        <Picker.Item label="Female" value="Female" />
      </Picker>

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
      <Picker
        selectedValue={form.bmiCategory}
        onValueChange={(v) => handleChange("bmiCategory", v)}
        style={styles.picker}
      >
        <Picker.Item label="Select Category" value="" />
        <Picker.Item label="Underweight" value="Underweight" />
        <Picker.Item label="Normal" value="Normal" />
        <Picker.Item label="Overweight" value="Overweight" />
        <Picker.Item label="Obese" value="Obese" />
      </Picker>

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
      <Picker
        selectedValue={form.sleepDisorder}
        onValueChange={(v) => handleChange("sleepDisorder", v)}
        style={styles.picker}
      >
        <Picker.Item label="Select Option" value="" />
        <Picker.Item label="None" value="None" />
        <Picker.Item label="Insomnia" value="Insomnia" />
        <Picker.Item label="Sleep Apnea" value="Sleep Apnea" />
      </Picker>

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
    marginBottom: 20,
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
  picker: {
    borderWidth: 1,
    borderColor: "#ccc",
    backgroundColor: "#f9f9f9",
    marginTop: 5,
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
