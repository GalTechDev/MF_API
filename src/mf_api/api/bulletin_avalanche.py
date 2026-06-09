from typing import Dict, Any, Union

from ..client import APISession

class BulletinAvalancheAPI:
    """
    Wrapper pour l'API Météo France - Bulletin Risque Avalanche (BRA)
    Services de téléchargement des bulletins d'estimation du risque d'avalanche les plus récents.
    """
    
    BASE_URL = "https://public-api.meteofrance.fr/public/DPBRA/v1"
    
    def __init__(self):
        self.headers = {"Accept": "application/json"}
        
    def get_liste_massifs(self) -> Dict[str, Any]:
        """
        Télécharger le fichier TEXTE (GeoJSON) de la liste des massifs.
        """
        url = f"{self.BASE_URL}/liste-massifs"
        response = APISession.get(url, headers=self.headers)
        response.raise_for_status()
        return response

    def get_bulletin_bra(self, id_massif: int, format: str = "xml") -> Union[Dict[str, Any], bytes, str]:
        """
        Télécharger le bulletin d'estimation du risque d'avalanche, en cours de validité, pour un massif.
        
        :param id_massif: L'identifiant du massif.
        :param format: 'xml' ou 'pdf'. Par défaut 'xml'.
        """
        url = f"{self.BASE_URL}/massif/BRA"
        params = {"id-massif": id_massif, "format": format}
        headers = {"Accept": "application/pdf"} if format.lower() == "pdf" else {"Accept": "application/xml"}
        
        response = APISession.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        if format.lower() == "pdf":
            return response
        return response

    def get_image_montagne_risques(self, id_massif: str) -> bytes:
        """Télécharger l'image de l'indice de risque du massif."""
        url = f"{self.BASE_URL}/massif/image/montagne-risques"
        params = {"id-massif": id_massif}
        response = APISession.get(url, headers={"Accept": "image/*"}, params=params)
        response.raise_for_status()
        return response

    def get_image_rose_pentes(self, id_massif: int) -> bytes:
        """Télécharger l'image de la rose des pentes du massif."""
        url = f"{self.BASE_URL}/massif/image/rose-pentes"
        params = {"id-massif": id_massif}
        response = APISession.get(url, headers={"Accept": "image/*"}, params=params)
        response.raise_for_status()
        return response

    def get_image_montagne_enneigement(self, id_massif: str) -> bytes:
        """Télécharger l'image de l'enneigement du massif."""
        url = f"{self.BASE_URL}/massif/image/montagne-enneigement"
        params = {"id-massif": id_massif}
        response = APISession.get(url, headers={"Accept": "image/*"}, params=params)
        response.raise_for_status()
        return response

    def get_image_graphe_neige_fraiche(self, id_massif: str) -> bytes:
        """Télécharger l'image du graphe de neige fraiche du massif."""
        url = f"{self.BASE_URL}/massif/image/graphe-neige-fraiche"
        params = {"id-massif": id_massif}
        response = APISession.get(url, headers={"Accept": "image/*"}, params=params)
        response.raise_for_status()
        return response

    def get_image_apercu_meteo(self, id_massif: str) -> bytes:
        """Télécharger l'image de l'aperçu météo du massif."""
        url = f"{self.BASE_URL}/massif/image/apercu-meteo"
        params = {"id-massif": id_massif}
        response = APISession.get(url, headers={"Accept": "image/*"}, params=params)
        response.raise_for_status()
        return response

    def get_image_sept_derniers_jours(self, id_massif: str) -> bytes:
        """Télécharger l'image des conditions météo des 7 derniers jours du massif."""
        url = f"{self.BASE_URL}/massif/image/sept-derniers-jours"
        params = {"id-massif": id_massif}
        response = APISession.get(url, headers={"Accept": "image/*"}, params=params)
        response.raise_for_status()
        return response
