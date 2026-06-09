import sys
import os
import tarfile

# Ajoute le dossier parent au chemin d'importation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()
import mf_api

mf_api.APISession.set_auth_token(os.getenv("TOKEN"))

paquetradarapi = mf_api.PaquetRadarAPI()

response = paquetradarapi.get_station_paquet(96)

content_disposition = response.headers.get('Content-Disposition')
if content_disposition:
    # Exemple de valeur : 'attachment; filename="radar_data.tar.gz"'
    # Il faut parser pour extraire le nom
    filename = content_disposition.split('filename=')[-1].strip('"')

FILE = f"bufr/data/{filename}"

with open(FILE, "wb") as f:
    f.write(response.content)

# 1. Extraire le .tar.gz
if not os.path.exists(FILE.removesuffix(".tar.gz")):
    with tarfile.open(FILE, "r:gz") as tar:
        tar.extractall(path=FILE.removesuffix(".tar.gz"))