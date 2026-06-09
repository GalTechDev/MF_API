from typing import Dict, Any, Optional
from ..client import APISession

class PIAFAPI:
    """
    Wrapper pour l'API Météo France - Modèle AROME PIAF
    """
    
    BASE_URL = "https://api.meteofrance.fr/pro/piaf/1.0"
    
    def __init__(self):
        self.headers = {"Accept": "application/json"}
        
    def get_capabilities(self, service: str = "WMS", version: str = "1.3.0", endpoint: str = "") -> bytes:
        """Obtenir les capacités du service (XML)."""
        url = f"{self.BASE_URL}/wms/{endpoint}/GetCapabilities" if service.upper() == "WMS" else f"{self.BASE_URL}/wcs/{endpoint}/GetCapabilities"
        params = {"service": service, "version": version}
        headers = {"Accept": "application/xml"}
        response = APISession.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.content

    def get_map(self, endpoint: str, layers: str, crs: str, bbox: str, width: int, height: int, format: str = "image/png", time: Optional[str] = None) -> bytes:
        url = f"{self.BASE_URL}/wms/{endpoint}/GetMap"
        params = {"service": "WMS", "version": "1.3.0", "layers": layers, "crs": crs, "bbox": bbox, "width": width, "height": height, "format": format, "transparent": "TRUE"}
        if time: params["time"] = time
        headers = {"Accept": format}
        response = APISession.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.content

    def get_coverage(self, endpoint: str, coverageid: str, subset: Optional[str] = None, format: str = "image/tiff") -> bytes:
        url = f"{self.BASE_URL}/wcs/{endpoint}/GetCoverage"
        params = {"service": "WCS", "version": "2.0.1", "coverageid": coverageid, "format": format}
        if subset: params["subset"] = subset
        headers = {"Accept": format}
        response = APISession.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.content
