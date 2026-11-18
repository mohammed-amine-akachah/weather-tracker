import logging
import sys
import requests
import pandas as pd
from datetime import datetime

# Configuration du logging (fichier + console)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("meteo.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

# Récupération des données par API
URL = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 34.6814,
    "longitude": -1.9086,
    "daily": "temperature_2m_max,temperature_2m_min",
    "timezone": "auto",
    "past_days": 1,
}

# Requête HTTP avec gestion complète des erreurs
try:
    response = requests.get(URL, params=params, timeout=10)
    logging.info(f"Code HTTP : {response.status_code}")
    response.raise_for_status()
    data = response.json()
except requests.exceptions.ConnectionError:
    logging.error("Pas de connexion Internet (ou serveur injoignable).")
    sys.exit(1)
except requests.exceptions.Timeout:
    logging.error("Délai dépassé : l'API met trop de temps à répondre.")
    sys.exit(1)
except requests.exceptions.HTTPError as e:
    logging.error(f"Réponse incorrecte de l'API : {e}")
    sys.exit(1)
except ValueError:
    logging.error("La réponse de l'API n'est pas un JSON valide.")
    sys.exit(1)
except requests.exceptions.RequestException as e:
    logging.error(f"Erreur de requête : {e}")
    sys.exit(1)

# Vérifications d'intégrité des données
if "daily" not in data:
    logging.error("Données incomplètes : la clé 'daily' est absente.")
    sys.exit(1)

for cle in ["time", "temperature_2m_max", "temperature_2m_min"]:
    if cle not in data["daily"]:
        logging.error(f"Données incomplètes : la clé '{cle}' est absente.")
        sys.exit(1)

tailles = {
    len(data["daily"][cle])
    for cle in ["time", "temperature_2m_max", "temperature_2m_min"]
}
if len(tailles) != 1 or 0 in tailles:
    logging.error("Données incomplètes : listes vides ou de tailles différentes.")
    sys.exit(1)

# Traitement automatique
dates    = data["daily"]["time"]
temp_max = data["daily"]["temperature_2m_max"]
temp_min = data["daily"]["temperature_2m_min"]

df = pd.DataFrame({
    "date":     dates,
    "temp_max": temp_max,
    "temp_min": temp_min,
})
df["temp_moy"] = (df["temp_max"] + df["temp_min"]) / 2

print("\n--- Tableau ---")
print(df)

print("\n--- Valeurs manquantes ---")
print(df.isna().sum())

manquantes = int(df.isna().sum().sum())
if manquantes > 0:
    logging.warning(f"{manquantes} valeur(s) manquante(s) : lignes supprimées.")
    df = df.dropna()

if df.empty:
    logging.error("Aucune donnée exploitable après nettoyage.")
    sys.exit(1)

moyenne = df["temp_moy"].mean()
minimum = df["temp_min"].min()
maximum = df["temp_max"].max()
date_min = df.loc[df["temp_min"].idxmin(), "date"]
date_max = df.loc[df["temp_max"].idxmax(), "date"]

# Le nombre de jours est calculé (et non codé en dur) : reste juste même
# si des lignes ont été supprimées par dropna().
print(f"\n--- Statistiques sur {len(df)} jours (1 jour précédent + jours à venir) ---")
print(f"Température moyenne  : {moyenne:.1f} °C")
print(f"Température minimale : {minimum:.1f} °C (le {date_min})")
print(f"Température maximale : {maximum:.1f} °C (le {date_max})")

# Génération automatique du fichier
VILLE = "Oujda"
date_generation = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

resume = pd.DataFrame({
    "Information": [
        "Ville",
        "Date de génération",
        "Période",
        "Température moyenne (°C)",
        "Température minimale (°C)",
        "Température maximale (°C)",
    ],
    "Valeur": [
        VILLE,
        date_generation,
        f"{df['date'].iloc[0]} au {df['date'].iloc[-1]}",
        round(moyenne, 1),
        round(minimum, 1),
        round(maximum, 1),
    ],
})

try:
    with open("meteo.csv", "w", encoding="utf-8-sig", newline="") as f:
        df.to_csv(f, index=False)
        f.write("\n")
        f.write("# --- Résumé ---\n")
        f.write("# Information,Valeur\n")
        for _, row in resume.iterrows():
            f.write(f"# {row['Information']},{row['Valeur']}\n")
    logging.info("Fichier généré : meteo.csv")
except PermissionError:
    logging.error("Impossible d'écrire : meteo.csv est ouvert dans Excel. Ferme-le.")
    sys.exit(1)
except OSError as e:
    logging.error(f"Erreur d'écriture du fichier : {e}")
    sys.exit(1)

# Vérification du fichier généré
print("\n--- Vérification du CSV (tableau de données) ---")
try:
    verif = pd.read_csv("meteo.csv", encoding="utf-8-sig", comment="#")
    print(verif)

    # Affichage du contenu brut pour vérifier aussi le résumé
    print("\n--- Vérification du CSV (contenu complet, résumé inclus) ---")
    with open("meteo.csv", encoding="utf-8-sig") as f:
        print(f.read())
except Exception as e:
    logging.error(f"Impossible de relire le fichier : {e}")
    sys.exit(1)