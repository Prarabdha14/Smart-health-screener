import pandas as pd
import pickle
from collections import Counter
import requests
import folium

# Load rules: maps question keys → list of diseases
with open(r"C:\Users\LENOVO\Desktop\main\question_to_symptoms.pkl", "rb") as f:
    question_to_diseases = pickle.load(f)

# Updated questions
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

def ask_questions():
    print("\nWelcome to the Smart Health Screener!")
    print("Please answer the following screening questions with 'Yes' or 'No'.\n")
    disease_counter = Counter()
    
    for key, question in questions.items():
        while True:
            answer = input(f"{question} ").strip().lower()
            if answer in ['yes', 'no']:
                if answer == 'yes':
                    # Use the rule to add diseases linked to this question
                    diseases = question_to_diseases.get(key, [])
                    disease_counter.update(diseases)
                break
            else:
                print("Please enter Yes or No.")
    return disease_counter

def predict_conditions(disease_counter):
    if not disease_counter:
        return ["No significant symptoms detected. Please consult a healthcare provider."]
    return [cond for cond, _ in disease_counter.most_common(3)]

# Hospital locator (same as before)
def get_nearby_hospitals_osm(latitude, longitude, radius=5000):
    print("\nSearching for hospitals via OpenStreetMap...")
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
            print("No hospitals found in OpenStreetMap data.")
            return False

        print("\nNearby Hospitals (via OpenStreetMap):")
        hospital_map = folium.Map(location=[latitude, longitude], zoom_start=13)
        folium.Marker([latitude, longitude], tooltip="Your Location", icon=folium.Icon(color='blue')).add_to(hospital_map)

        for el in elements[:10]:
            name = el.get("tags", {}).get("name", "Unnamed Hospital")
            lat = el.get("lat", el.get("center", {}).get("lat", None))
            lon = el.get("lon", el.get("center", {}).get("lon", None))
            if lat and lon:
                print(f"{name}, Location: ({lat}, {lon})")
                folium.Marker([lat, lon], popup=name, icon=folium.Icon(color='red')).add_to(hospital_map)

        hospital_map.save("nearby_hospitals_map.html")
        print("\n📍 Map saved as 'nearby_hospitals_map.html'. Open it in your browser.")
        return True

    except Exception as e:
        print(f"OpenStreetMap API error: {e}")
        return False

def show_hospitals_from_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        print("\nNearby Hospitals (Offline Database):")
        for i, row in df.head(5).iterrows():
            print(f"{row['Hospital']}, {row['City']} ({row['State']})")
    except Exception as e:
        print(f"Error loading hospital list: {e}")

def main():
    hospital_csv = r'C:\Users\LENOVO\Desktop\main\HospitalsInIndia_1.csv'

    detected_diseases = ask_questions()
    top_conditions = predict_conditions(detected_diseases)

    print("\nDiagnosis Result:")
    for condition in top_conditions:
        print(f"⚠️ Possible Condition: {condition}")

    try:
        print("\nNote: Latitude comes first (e.g., 28.6), then Longitude (e.g., 77.3)")
        latitude = float(input("Enter your current latitude: ").strip())
        longitude = float(input("Enter your current longitude: ").strip())
        success = get_nearby_hospitals_osm(latitude, longitude)
        if not success:
            print("Using offline hospital data instead.")
            show_hospitals_from_csv(hospital_csv)
    except Exception as e:
        print(f"Location input error: {e}")
        show_hospitals_from_csv(hospital_csv)

if __name__ == "__main__":
    main()