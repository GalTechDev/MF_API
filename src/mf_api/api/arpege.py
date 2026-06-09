from typing import Dict, Any, Optional

from ..client import APISession

class ArpegeAPI:
    """
    Wrapper pour l'API Météo France - Modèle ARPEGE (WMS / WCS)
    Basé sur Modèle_ARPEGE_swagger.json
    """
    
    # URL de base pour les requêtes WMS et WCS
    # Les URL réelles incluent l'endpoint spécifique comme /wms/MF-NWP-GLOBAL-ARPEGE-01-EUROPE-WMS/
    BASE_URL = "https://public-api.meteofrance.fr/public/arpege/v1"
    
    def __init__(self):
        self.headers = {"Accept": "application/json"}
        
    def get_capabilities(self, service: str = "WMS", version: str = "1.3.0", endpoint: str = "MF-NWP-GLOBAL-ARPEGE-01-EUROPE-WMS") -> bytes:
        """Obtenir les capacités du service (XML)."""
        url = f"{self.BASE_URL}/wms/{endpoint}/GetCapabilities" if service.upper() == "WMS" else f"{self.BASE_URL}/wcs/{endpoint}/GetCapabilities"
        params = {
            "service": service,
            "version": version,
        }
        headers = {"Accept": "application/xml"}
        response = APISession.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response

    def get_map(self, endpoint: str, layers: str, crs: str, bbox: str, width: int, height: int, format: str = "image/png", time: Optional[str] = None) -> bytes:
        """
        Requête WMS GetMap pour récupérer une image cartographique.
        
        :param endpoint: Nom du service WMS (ex: MF-NWP-GLOBAL-ARPEGE-01-EUROPE-WMS)
        :param layers: Nom de la couche (ex: TEMPERATURE__ISOBARIC_SURFACE)
        :param crs: Système de coordonnées (ex: EPSG:4326)
        :param bbox: Bounding box "min_lon,min_lat,max_lon,max_lat"
        :param width: Largeur en pixels
        :param height: Hauteur en pixels
        """
        url = f"{self.BASE_URL}/wms/{endpoint}/GetMap"
        params = {
            "service": "WMS",
            "version": "1.3.0",
            "layers": layers,
            "crs": crs,
            "bbox": bbox,
            "width": width,
            "height": height,
            "format": format,
            "transparent": "TRUE"
        }
        if time:
            params["time"] = time
            
        headers = {"Accept": format}
        response = APISession.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response

    def get_coverage(self, endpoint: str, coverageid: str, subset: Optional[str] = None, format: str = "image/tiff") -> bytes:
        """
        Requête WCS GetCoverage pour récupérer les données brutes.
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
