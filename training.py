import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier
import pickle

# Define the dataset
data = pd.read_csv(r'C:\Users\LENOVO\Desktop\main\patient_symptom_dataset.csv')

# Column names
columns = [
    "Thirst", "Frequent_Urination", "Weight_Loss", "Fatigue", "Chest_Pain", "Snoring",
    "Morning_Headache", "High_BP", "Short_Breath", "Persistent_Cough", "Depressed_Mood",
    "Concentration_Issues", "Weight_Gain", "Swelling", "Joint_Pain", "Indigestion",
    "Jaundice", "Unhealthy_Diet", "High_Cholesterol", "Feel_Cold", "Appearance_Changes",
    "Alcohol_Use", "Liver_History", "Exercise_Low", "Family_History", "Diseases"
]

# Create DataFrame
df = pd.DataFrame(data, columns=columns)

# Separate features and target
X = df.drop(columns=["Diseases"])
y = df["Diseases"]

# Clean and format target labels
y = y.apply(lambda x: ', '.join([label.strip() for label in x.split(',')]))

# Convert features to numeric
X = X.apply(pd.to_numeric, errors='coerce').fillna(0)

# Encode multiple diseases
mlb = MultiLabelBinarizer()
y_encoded = mlb.fit_transform(y.str.split(", "))

# Train-Test Split (optional, good for evaluation)
# X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Train the model
tree_model = MultiOutputClassifier(DecisionTreeClassifier(max_depth=4, random_state=42))
tree_model.fit(X, y_encoded)

# Display rules
print("Generated Rules from the Model:")
for i, disease in enumerate(mlb.classes_):
    print(f"\n📘 Rules for {disease}:")
    tree = tree_model.estimators_[i]
    rules = export_text(tree, feature_names=list(X.columns))
    print(rules)

# Save the model
with open("decision_tree_model.pkl", "wb") as f:
    pickle.dump(tree_model, f)

# Save the label encoder
with open("question_to_symptom.pkl", "wb") as f:
    pickle.dump(mlb, f)

# Optional: Function to load model
def load_model(model_path="decision_tree_model.pkl"):
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None
