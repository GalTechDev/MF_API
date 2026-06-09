from typing import Dict, Any

from ..client import APISession

class PaquetRadarAPI:
    """
    Wrapper pour l'API Météo France - DonneesPubliquesPaquetRadar
    Basé sur les spécifications OpenAPI fournies.
    """
    
    BASE_URL = "https://public-api.meteofrance.fr/public/DPPaquetRadar/v1"
    
    def __init__(self):
        self.headers = {
            "Accept": "application/json"
        }
        
    def get_mosaique_paquet(self) -> bytes:
        """
        Télécharger le paquet du dernier 1/4h des données mosaïque radar de précipitation.
        Retourne les données brutes (GZIP contenant les fichiers BUFR/HDF5).
        """
        url = f"{self.BASE_URL}/mosaique/paquet"
        headers = {}
        headers["Accept"] = "application/gzip"
        
        response = APISession.get(url, headers=headers)
        response.raise_for_status()
        return response

    def get_liste_stations(self) -> str:
        """
        Télécharger la liste des stations radar.
        Retourne le contenu CSV sous forme de chaîne de caractères.
        """
        url = f"{self.BASE_URL}/liste-stations"
        headers = {}
        headers["Accept"] = "text/csv"
        
        response = APISession.get(url, headers=headers)
        response.raise_for_status()
        return response.text

    def get_stations(self) -> Dict[str, Any]:
        """
        Télécharger la liste des stations disponibles au format JSON.
        """
        url = f"{self.BASE_URL}/stations"
        
        response = APISession.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_station_paquet(self, id_station: int) -> bytes:
        """
        Télécharger le paquet du dernier 1/4h des données d'un radar individuel.
        Retourne les données brutes (GZIP contenant les 6 fichiers BUFR concaténés).
        
        :param id_station: L'identifiant de la station (entier, ex: 36)
        """
        url = f"{self.BASE_URL}/station/paquet"
        headers = {}
        headers["Accept"] = "application/octet-stream+gzip"
        params = {"id_station": id_station}
        
        response = APISession.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response

