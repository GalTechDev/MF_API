from typing import Dict, Any, Optional

from ..client import APISession

class PEAromeAPI:
    """
    Wrapper pour l'API Météo France - Prévision d'Ensemble AROME (WMS / WCS)
    Basé sur Modèle_AROME_Prévision_d'Ensemble_swagger.json
    """
    
    BASE_URL = "https://public-api.meteofrance.fr/public/pearome/1.0"
    
    def __init__(self):
        self.headers = {"Accept": "application/json"}
        
    def get_capabilities(self, service: str = "WCS", version: str = "2.0.1", endpoint: str = "MF-NWP-HIGHRES-PEARO-0025-FRANCE-WCS") -> bytes:
        """Obtenir les capacités du service (XML)."""
        url = f"{self.BASE_URL}/wcs/{endpoint}/GetCapabilities" if service.upper() == "WCS" else f"{self.BASE_URL}/wms/{endpoint}/GetCapabilities"
        params = {
            "service": service,
            "version": version,
        }
        headers = {"Accept": "application/xml"}
        response = APISession.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response

    def get_coverage(self, endpoint: str, coverageid: str, subset: Optional[str] = None, format: str = "image/tiff") -> bytes:
        """
        Requête WCS GetCoverage pour récupérer les données brutes (GRIB/NetCDF/TIFF).
        """
        url = f"{self.BASE_URL}/wcs/{endpoint}/GetCoverage"
        params = {
            "service": "WCS",
            "version": "2.0.1",
            "coverageid": coverageid,
            "format": format
        }
        if subset:
            params["subset"] = subset
            
        headers = {"Accept": format}
        response = APISession.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response
