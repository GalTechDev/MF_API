from typing import Dict, Any

from ..client import APISession

class PaquetArpegeAPI:
    """
    Wrapper pour l'API Météo France - Paquet ARPEGE
    Basé sur la documentation Swagger (Package_ARPEGE_swagger.json)
    """
    
    BASE_URL = "https://public-api.meteofrance.fr/previnum/DPPaquetARPEGE/v1"
    
    def __init__(self):
        self.headers = {"Accept": "application/json"}
        
    def get_models(self) -> Dict[str, Any]:
        """Obtenir les modèles de base."""
        url = f"{self.BASE_URL}/models/ARPEGE"
        response = APISession.get(url, headers=self.headers)
        response.raise_for_status()
        return response

    def get_grids(self) -> Dict[str, Any]:
        """Obtenir la liste des grilles disponibles."""
        url = f"{self.BASE_URL}/models/ARPEGE/grids"
        response = APISession.get(url, headers=self.headers)
        response.raise_for_status()
        return response

    def get_grid_details(self, grid: float) -> Dict[str, Any]:
        """Obtenir les détails d'une grille spécifique."""
        url = f"{self.BASE_URL}/models/ARPEGE/grids/{grid}"
        response = APISession.get(url, headers=self.headers)
        response.raise_for_status()
        return response

    def get_packages(self, grid: float) -> Dict[str, Any]:
        """Obtenir les paquets disponibles pour une grille donnée."""
        url = f"{self.BASE_URL}/models/ARPEGE/grids/{grid}/packages"
        response = APISession.get(url, headers=self.headers)
        response.raise_for_status()
        return response

    def get_package_details(self, grid: float, package: str, referencetime: str) -> Dict[str, Any]:
        """Obtenir les détails d'un paquet."""
        url = f"{self.BASE_URL}/models/ARPEGE/grids/{grid}/packages/{package}"
        params = {"referencetime": referencetime}
        response = APISession.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response

    def get_product(self, grid: float, package: str, referencetime: str, time: str, format: str = "GRIB2") -> bytes:
        """
        Télécharger les données météorologiques sous forme de produit binaire (grib2).
        
        :param grid: La grille de données
        :param package: Le nom du paquet
        :param referencetime: Date du run au format YYYY-MM-DDTHH:MM:SSZ
        :param time: Echéance de prévision au format YYYY-MM-DDTHH:MM:SSZ
        :param format: Le format attendu (généralement 'GRIB2')
        """
        url = f"{self.BASE_URL}/productARP"
        params = {
            "grid": grid,
            "package": package,
            "referencetime": referencetime,
            "time": time,
            "format": format
        }
        headers = {"Accept": "application/octet-stream"}
        response = APISession.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response
