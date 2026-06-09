from typing import Dict, Any, Optional
from ..client import APISession

class ClimatologieAPI:
    """
    Wrapper pour l'API Météo France - Données Climatologiques
    """
    
    BASE_URL = "https://public-api.meteofrance.fr/public/DPClim/v1"
    
    def __init__(self):
        self.headers = {"Accept": "application/json"}
        
    # TODO: Ajouter les requêtes spécifiques en fonction des endpoints
    # Exemple générique:
    def get_data(self, endpoint: str = "", params: dict = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{endpoint}" if endpoint else self.BASE_URL
        response = APISession.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
