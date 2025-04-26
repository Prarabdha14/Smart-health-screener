import streamlit as st
import pandas as pd
import pickle
from collections import Counter
import requests
import folium
from streamlit_folium import st_folium

# Load data
with open("/Users/prarabdhapandey/Documents/virat/question_to_symptoms.pkl", "rb") as f:
    question_to_diseases = pickle.load(f)

hospital_csv = '/Users/prarabdhapandey/Documents/virat/HospitalsInIndia_1.csv'

questions = { 
     "Thirst": "Do you often feel excessively thirsty or have a dry mouth?",
    "Frequent_Urination": "Do you urinate more frequently than usual, especially at night?",
    "Weight_Loss": "Have you experienced unexplained weight loss recently?",
    "Fatigue": "Do you feel tired or fatigued most of the time, even with enough sleep?",
    "Chest_Pain": "Do you frequently experience chest pain or tightness during activity?",
    "Snoring": "Do you snore loudly or stop breathing while sleeping (observed by others)?",
    "Morning_Headache": "Do you often wake up with a headache or dry mouth?",
    "High_BP": "Have you ever been diagnosed with high blood pressure?",
    "Short_Breath": "Do you feel short of breath during light physical activity or rest?",
    "Persistent_Cough": "Do you have a persistent cough, especially with mucus?",
    "Depressed_Mood": "Do you feel sad, hopeless, or uninterested in daily activities for more than two weeks?",
    "Concentration_Issues": "Do you have trouble concentrating or remembering things?",
    "Weight_Gain": "Have you gained weight recently without a major change in diet or activity?",
    "Swelling": "Do you experience swelling in your ankles, feet, or face?",
    "Joint_Pain": "Do your joints ache or feel stiff, especially in the morning?",
    "Indigestion": "Do you have frequent indigestion, heartburn, or acid reflux?",
    "Jaundice": "Have you noticed yellowing of your skin or eyes (jaundice)?",
    "Unhealthy_Diet": "Is your diet high in processed, fried, or sugary foods?",
    "High_Cholesterol": "Have you ever been told your cholesterol or triglyceride levels are high?",
    "Feel_Cold": "Do you feel cold more often than others, even in warm settings?",
    "Appearance_Changes": "Do you have brittle nails, pale skin, or hair loss?",
    "Alcohol_Use": "Do you consume alcohol regularly (more than 3-4 times per week)?",
    "Liver_History": "Have you had hepatitis or known liver issues in the past?",
    "Exercise_Low": "Do you exercise less than 3 times per week?",
    "Family_History": "Do you have a family history of heart disease, diabetes, or thyroid issues?"
} 


# Functions
def predict_conditions(disease_counter):
    if not disease_counter:
        return ["No significant symptoms detected. Please consult a healthcare provider."]
    return [cond for cond, _ in disease_counter.most_common(3)]

def get_nearby_hospitals_osm(latitude, longitude, radius=5000):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:{radius},{latitude},{longitude});
      way["amenity"="hospital"](around:{radius},{latitude},{longitude});
      relation["amenity"="hospital"](around:{radius},{latitude},{longitude});
    );
    out center;
    """
    try:
        response = requests.post(overpass_url, data={"data": query})
        data = response.json()
        elements = data.get("elements", [])

        if not elements:
            return None

        hospital_map = folium.Map(location=[latitude, longitude], zoom_start=13)
        folium.Marker([latitude, longitude], tooltip="Your Location", icon=folium.Icon(color='blue')).add_to(hospital_map)

        for el in elements[:10]:
            name = el.get("tags", {}).get("name", "Unnamed Hospital")
            lat = el.get("lat", el.get("center", {}).get("lat", None))
            lon = el.get("lon", el.get("center", {}).get("lon", None))
            if lat and lon:
                folium.Marker([lat, lon], popup=name, icon=folium.Icon(color='red')).add_to(hospital_map)

        return hospital_map

    except Exception as e:
        st.error(f"OpenStreetMap API error: {e}")
        return None

def show_hospitals_from_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        return df.head(5)
    except Exception as e:
        st.error(f"Error loading hospital list: {e}")
        return None

# Streamlit app
def main():
    st.title("🩺 Smart Health Screener")
    st.subheader("Answer the following questions:")

    disease_counter = Counter()

    # Ask each question
    for key, question in questions.items():
        answer = st.radio(f"{question}", ("Yes", "No"), key=key)
        if answer == "Yes":
            diseases = question_to_diseases.get(key, [])
            disease_counter.update(diseases)

    if st.button("Predict Health Conditions"):
        top_conditions = predict_conditions(disease_counter)
        
        st.subheader("Diagnosis Result:")
        for condition in top_conditions:
            st.write(f"⚠️ Possible Condition: {condition}")

        st.subheader("Find Nearby Hospitals:")

        latitude = st.number_input("Enter your latitude:", format="%.6f")
        longitude = st.number_input("Enter your longitude:", format="%.6f")
        
        if latitude != 0.0 and longitude != 0.0:
            hospital_map = get_nearby_hospitals_osm(latitude, longitude)
            if hospital_map:
                st_folium(hospital_map, width=700, height=500)
            else:
                st.warning("No hospitals found online, showing offline database instead.")
                df = show_hospitals_from_csv(hospital_csv)
                if df is not None:
                    st.dataframe(df)

if __name__ == "__main__":
    main()
