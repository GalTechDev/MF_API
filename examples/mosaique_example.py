from dask.array.core import A
import os
import sys
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from mf_api.decoders.mosaique_decoder import MosaiqueDecoder
from mf_api import APISession
from dotenv import load_dotenv
load_dotenv()

APISession.set_auth_token(os.getenv("TOKEN"))
print(APISession.get_api_key())
# Chemin vers un fichier BUFR/LZW local existant pour le test
BUFR_FILE = "s:/Code/Python/MF_API/bufr/data/paquetradar_station_96_20260604224500/T_PAHM43_C_NWWL_20260604223500.bufr.gz"

def example_mosaique_bufr():
    print("=== Test de décodage Mosaïque (Format BUFR / LZW) ===")
    if not os.path.exists(BUFR_FILE):
        print(f"Fichier {BUFR_FILE} introuvable.")
        return
        
    with open(BUFR_FILE, 'rb') as f:
        raw_data = f.read()

    try:
        mos = MosaiqueDecoder.decode(raw_data, format_attendu="bufr", nom_produit="PAHM43", maille_m=1000)
        
        print(f"Produit décodé : {mos.nom_produit}")
        print(f"Date d'observation : {mos.date_observation}")
        print(f"Dimensions de la grille : {mos.shape}")
        
        # Génération d'une image pour valider le contenu
        plt.figure(figsize=(8, 8))
        plt.imshow(mos.data, cmap='nipy_spectral', vmin=-10, vmax=60)
        plt.colorbar(label='dBZ')
        plt.title(f'Mosaïque {mos.nom_produit} (BUFR) - {mos.date_observation}')
        
        output_name = "mosaique_test_bufr.png"
        plt.savefig(output_name)
        print(f"Image sauvegardée sous {output_name}")
        plt.close()
    except Exception as e:
        print("Erreur lors du décodage BUFR :", e)

def example_mosaique_api():
    """
    Exemple d'utilisation de l'API pour télécharger une mosaïque au format HDF5.
    Cet exemple nécessite que les variables d'environnement (ex: APPLICATION_ID) soient configurées.
    """
    print("\n=== Test de décodage Mosaïque (Via API - Format HDF5) ===")
    from mf_api.api.radar import RadarAPI
    
    try:
        api = RadarAPI()
        # On va chercher la mosaïque métropole (par exemple 'metropole', 'REFLECTIVITE')
        # Ce test est entouré d'un try-except en cas d'absence d'authentification
        mos = api.get_mosaique_produit_decode(
            zone="METROPOLE", 
            observation="REFLECTIVITE", 
            maille=1000, 
            format_attendu="bufr" # L'API ne propose que du GZIP/BUFR pour la métropole
        )
        
        print(f"Produit décodé : {mos.nom_produit}")
        print(f"Dimensions de la grille : {mos.shape}")
        
        plt.figure(figsize=(8, 8))
        plt.imshow(mos.data, cmap='nipy_spectral', vmin=-10, vmax=60)
        plt.colorbar(label='dBZ')
        plt.title(f'Mosaïque {mos.nom_produit} (HDF5)')
        
        output_name = "mosaique_test_hdf5.png"
        plt.savefig(output_name)
        print(f"Image sauvegardée sous {output_name}")
        plt.close()
    except Exception as e:
        print("L'appel à l'API a échoué (authentification manquante ou données non trouvées) :", e)


if __name__ == "__main__":
    example_mosaique_bufr()
    example_mosaique_api()
