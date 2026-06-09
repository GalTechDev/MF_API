from typing import Dict, Any, Optional

from ..client import APISession

class RadarAPI:
    """
    Wrapper pour l'API Météo France - DonneesPubliquesRadar
    Basé sur les spécifications OpenAPI fournies.
    """
    
    BASE_URL = "https://public-api.meteofrance.fr/public/DPRadar/v1"
    
    def __init__(self):
        self.headers = {
            "Accept": "application/json"
        }

    # ==========================================
    # Produits Radar Mosaïque
    # ==========================================

    def get_mosaiques(self) -> Dict[str, Any]:
        """Télécharger la liste des zones de mosaïques disponibles."""
        url = f"{self.BASE_URL}/mosaiques"
        response = APISession.get(url, headers=self.headers)
        response.raise_for_status()
        return response

    def get_zone_mosaiques(self, zone: str) -> Dict[str, Any]:
        """Obtenir la description de la zone."""
        url = f"{self.BASE_URL}/mosaiques/{zone}"
        response = APISession.get(url, headers=self.headers)
        response.raise_for_status()
        return response

    def get_produits_mosaiques(self, zone: str) -> Dict[str, Any]:
        """Télécharger la liste des observations disponibles pour la zone spécifiée."""
        url = f"{self.BASE_URL}/mosaiques/{zone}/observations"
        response = APISession.get(url, headers=self.headers)
        response.raise_for_status()
        return response

    def descr_produits_mosaiques(self, zone: str, observation: str) -> Dict[str, Any]:
        """Obtenir la description de l'observation mosaïque disponible."""
        url = f"{self.BASE_URL}/mosaiques/{zone}/observations/{observation}"
        response = APISession.get(url, headers=self.headers)
        response.raise_for_status()
        return response

    def get_mosaique_produit(self, zone: str, observation: str, maille: int, format_attendu: str = "gzip") -> bytes:
        """
        Télécharger le fichier des données mosaïque radar de précipitation.
        
        :param zone: La zone de la mosaïque (ex: 'metropole')
        :param observation: L'observation spécifique
        :param maille: Maille en mètres (ex: 1000)
        :param format_attendu: Format attendu: "gzip" (BUFR zippé) ou "hdf" (HDF5)
        """
        url = f"{self.BASE_URL}/mosaiques/{zone}/observations/{observation}/produit"
        params = {"maille": maille}
        headers = {}
        
        if format_attendu == "hdf":
            headers["Accept"] = "application/x-hdf"
        else:
            headers["Accept"] = "application/octet-stream+gzip"
            
        response = APISession.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response

    def get_mosaique_produit_decode(self, zone: str, observation: str, maille: int, format_attendu: str = "gzip"):
        """
        Télécharger et décoder la mosaïque directement.
        Retourne un objet MosaiqueRadar.
        """
        raw_bytes = self.get_mosaique_produit(zone, observation, maille, format_attendu).content
        
        from ..decoders.mosaique_decoder import MosaiqueDecoder
        return MosaiqueDecoder.decode(raw_bytes, format_attendu, nom_produit=observation, maille_m=maille)

    # ==========================================
    # Produits Radar Individuel
    # ==========================================

    def get_liste_stations(self) -> str:
        """
        Télécharger la liste complète des stations radar.
        Retourne le contenu CSV sous forme de chaîne.
        """
        url = f"{self.BASE_URL}/liste-stations"
        headers = {}
        headers["Accept"] = "text/csv"
        
        response = APISession.get(url, headers=headers)
        response.raise_for_status()
        return response

    def get_stations(self) -> Dict[str, Any]:
        """Télécharger la liste des stations disponibles."""
        url = f"{self.BASE_URL}/stations"
        response = APISession.get(url, headers=self.headers)
        response.raise_for_status()
        return response

    def get_station_info(self, id_station: int) -> Dict[str, Any]:
        """Obtenir la description de la station."""
        url = f"{self.BASE_URL}/stations/{id_station}"
        response = APISession.get(url, headers=self.headers)
        response.raise_for_status()
        return response

    def get_station_obs(self, id_station: int) -> Dict[str, Any]:
        """Télécharger la liste des observations disponibles pour la station spécifiée."""
        url = f"{self.BASE_URL}/stations/{id_station}/observations"
        response = APISession.get(url, headers=self.headers)
        response.raise_for_status()
        return response

    def get_station_obs_descr(self, id_station: int, observation: str) -> Dict[str, Any]:
        """Obtenir la description de l'observation pour la station spécifiée."""
        url = f"{self.BASE_URL}/stations/{id_station}/observations/{observation}"
        response = APISession.get(url, headers=self.headers)
        response.raise_for_status()
        return response

    def get_polaires(self, id_station: int, observation: str, tour_antenne: Optional[str] = None) -> bytes:
        """
        Télécharger le fichier des données de précipitations du radar individuel.
        
        :param id_station: Identifiant de la station
        :param observation: Nom de l'observation
        :param tour_antenne: Un caractère (A-H). Obligatoire pour les observations PAM et PAG.
        """
        url = f"{self.BASE_URL}/stations/{id_station}/observations/{observation}/produit"
        headers = {}
        headers["Accept"] = "application/octet-stream+gzip"
        
        params = {}
        if tour_antenne:
            params["tour_antenne"] = tour_antenne
            
        response = APISession.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response
