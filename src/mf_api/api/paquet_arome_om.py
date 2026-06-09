from typing import Dict, Any, Optional
from ..client import APISession

class PaquetAromeOMAPI:
    """
    Wrapper pour l'API Météo France - Package AROME Outre-mer
    """
    
    BASE_URL = "https://public-api.meteofrance.fr/previnum/DPPaquetAROME-OM/v1"
    
    def __init__(self):
        self.headers = {"Accept": "application/json"}
        
    def get_capabilities(self) -> Dict[str, Any]:
        """Obtenir les capacités du package."""
        url = f"{self.BASE_URL}/"
        # Nettoyage si base_url se termine déjà par /
        if url.endswith("//"): url = url[:-1]
        response = APISession.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
