from typing import Dict, Any

from ..client import APISession

class PaquetAromeAPI:
    """
    Wrapper pour l'API Météo France - Paquet AROME
    Basé sur la documentation Swagger (Package_AROME_swagger.json)
    """
    
    BASE_URL = "https://public-api.meteofrance.fr/previnum/DPPaquetAROME/v1"
    
    def __init__(self):
        self.headers = {"Accept": "application/json"}
        
    def get_models(self) -> Dict[str, Any]:
        """Obtenir les modèles de base."""
        url = f"{self.BASE_URL}/models/AROME"
        response = APISession.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_grids(self) -> Dict[str, Any]:
        """Obtenir la liste des grilles disponibles."""
        url = f"{self.BASE_URL}/models/AROME/grids"
        response = APISession.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_grid_details(self, grid: float) -> Dict[str, Any]:
        """Obtenir les détails d'une grille spécifique."""
        url = f"{self.BASE_URL}/models/AROME/grids/{grid}"
        response = APISession.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_packages(self, grid: float) -> Dict[str, Any]:
        """Obtenir les paquets disponibles pour une grille donnée."""
        url = f"{self.BASE_URL}/models/AROME/grids/{grid}/packages"
        response = APISession.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_package_details(self, grid: float, package: str, referencetime: str) -> Dict[str, Any]:
        """Obtenir les détails d'un paquet."""
        url = f"{self.BASE_URL}/models/AROME/grids/{grid}/packages/{package}"
        params = {"referencetime": referencetime}
        response = APISession.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_product(self, grid: float, package: str, referencetime: str, time: str, format: str = "GRIB2") -> bytes:
        """
        Télécharger les données météorologiques sous forme de produit binaire (grib2).
        
        :param grid: La grille de données (ex: 0.01, 0.025, 0.1)
        :param package: Le nom du paquet (ex: SP1, HP1)
        :param referencetime: Date du run au format YYYY-MM-DDTHH:MM:SSZ
        :param time: Echéance de prévision au format YYYY-MM-DDTHH:MM:SSZ
        :param format: Le format attendu (généralement 'GRIB2')
        """
        url = f"{self.BASE_URL}/productARO"
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
        return response.content
