import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Charge les variables définies dans ton fichier .env local
load_dotenv()

USERNAME = "00cd5b100b3021296f168181cfb8d524"
# Récupère le mot de passe depuis le .env ; utilise la valeur par défaut si non trouvé
PASSWORD = os.getenv("RAVELRY_PASSWORD", "VOTRE_CLE_SECRETE")

url = "https://api.ravelry.com/patterns/search.json"
params = {"query": "bandana", "page_size": 5}
headers = {"User-Agent": "YarnMatch/1.0"}

print("Envoi de la requête...")
response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), params=params, headers=headers)

print(f"Statut HTTP : {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print("Succès ! Voici le premier patron :", data['patterns'][0]['name'])
else:
    print(f"Erreur : {response.text}")