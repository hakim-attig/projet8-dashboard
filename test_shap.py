import pandas as pd
import requests

# --- CONFIGURATION ---
CSV_PATH = "C:/Users/amine/Desktop/projet_openclassrooms/projet8-dashboard/data/all_clients_test_sample.csv"
API_URL = "https://api-scoring-credit-final.onrender.com/explain"

# --- CHARGER LES DONNÉES ---
df = pd.read_csv(CSV_PATH)
print(f"Nombre de clients dans le sample : {len(df)}")

# --- CHOISIR LE CLIENT SPÉCIFIQUE ---
client_id = 100257
if client_id not in df["SK_ID_CURR"].values:
    raise ValueError(f"Client {client_id} non trouvé dans le CSV.")

client_row = df[df["SK_ID_CURR"] == client_id].iloc[0]

# --- EXTRAIRE LES FEATURES ---
features_to_drop = ["SK_ID_CURR", "RISK_SCORE", "DECISION", "REAL_TARGET"]
features = client_row.drop(features_to_drop, errors="ignore").values.tolist()

# --- CONVERTIR EN FLOAT PYTHON STANDARD ---
features = [float(x) for x in features]

print(f"Nombre de features envoyées : {len(features)}")
print(f"Exemple de features : {features[:10]}")  # Affiche les 10 premières valeurs

# --- ENVOYER À L'API /explain ---
response = requests.post(API_URL, json={"features": features})

# --- AFFICHER LE RÉSULTAT ---
print("Status code:", response.status_code)

try:
    print("Réponse JSON:", response.json())
except Exception:
    print("Impossible de décoder la réponse en JSON :", response.text)
