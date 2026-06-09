import io
import numpy as np
try:
    import h5py
except ImportError:
    h5py = None

try:
    import unlzw3
except ImportError:
    unlzw3 = None

from .eccodes_decoder import MFBufrDecoder
from dataclasses import dataclass
from typing import Tuple, Any

@dataclass
class MosaiqueRadar:
    nom_produit: str
    maille_m: int
    data: Any
    date_observation: str = None
    lat_min: float = None
    lat_max: float = None
    lon_min: float = None
    lon_max: float = None
    
    @property
    def shape(self) -> Tuple[int, int]:
        return self.data.shape if self.data is not None else (0, 0)

class MosaiqueDecoder:
    """
    Décodeur universel pour les fichiers de mosaïque radar.
    Supporte les formats HDF5 et BUFR (compressé LZW / .Z).
    """

    @staticmethod
    def decode_hdf5(raw_bytes: bytes, nom_produit: str, maille_m: int) -> MosaiqueRadar:
        if h5py is None:
            raise ImportError("La librairie h5py est requise pour lire le format HDF5. (pip install h5py)")
        
        # Le format HDF5 de Météo France pour la mosaïque contient le dataset "dataset1/data1/data"
        with h5py.File(io.BytesIO(raw_bytes), 'r') as h5f:
            # L'arborescence standard ODIM_H5
            if "dataset1" in h5f and "data1" in h5f["dataset1"] and "data" in h5f["dataset1"]["data1"]:
                dataset = h5f["dataset1"]["data1"]["data"]
                
                # Les données sont généralement scalées
                gain = dataset.attrs.get("gain", 1.0)
                offset = dataset.attrs.get("offset", 0.0)
                nodata = dataset.attrs.get("nodata", 255)
                
                raw_data = dataset[:]
                data = np.full(raw_data.shape, np.nan, dtype=np.float32)
                
                valide = raw_data != nodata
                data[valide] = (raw_data[valide] * gain) + offset
                
                # Extraction des informations géographiques (facultatif si non présentes)
                where = h5f.get("where")
                lat_min, lat_max, lon_min, lon_max = None, None, None, None
                if where:
                    # En ODIM_H5, on a souvent projdef, xscale, yscale, LL_lon, LL_lat etc.
                    pass 
                
                return MosaiqueRadar(
                    nom_produit=nom_produit,
                    maille_m=maille_m,
                    data=data,
                    lat_min=lat_min, lat_max=lat_max,
                    lon_min=lon_min, lon_max=lon_max
                )
            else:
                raise ValueError("Structure HDF5 non reconnue (ODIM_H5 attendu)")

    @staticmethod
    def decode_bufr(raw_bytes: bytes, nom_produit: str, maille_m: int) -> MosaiqueRadar:
        import gzip
        # 1. Vérifier si c'est compressé en LZW (.Z) ou GZIP (.gz)
        if raw_bytes.startswith(b'\x1f\x9d'):
            if unlzw3 is None:
                raise ImportError("La librairie unlzw3 est requise pour décompresser le format LZW (.Z). (pip install unlzw3)")
            bufr_data = unlzw3.unlzw(raw_bytes)
        elif raw_bytes.startswith(b'\x1f\x8b'):
            bufr_data = gzip.decompress(raw_bytes)
        else:
            bufr_data = raw_bytes

        # 2. Décoder avec eccodes_decoder
        decoded = MFBufrDecoder.decode(bufr_data)
        
        if not decoded or "numericValues" not in decoded:
            raise ValueError("Le décodage BUFR n'a pas pu extraire de numericValues.")
            
        arr = np.array(decoded["numericValues"])
        
        # Pour une mosaïque 1km de la métropole, la grille fait 1536 x 1536
        # Si la maille est 2km, la grille pourrait être 768 x 768
        
        # Déduction dynamique de la taille de l'image (les pixels sont toujours à la fin)
        # On essaie les dimensions connues:
        sizes = [(1536, 1536), (768, 768), (3072, 3072), (512, 512)]
        
        data_2d = None
        for (h, w) in sizes:
            expected = h * w
            if len(arr) >= expected:
                # Météo France encode les images 1km sur 1536x1536
                raw_pixels = arr[-expected:].reshape((h, w))
                
                # Application de la formule spécifique (Réflectivité Z) : 
                # -11 + code, et les codes de 0 à 79 sont valides
                z_dbz = np.full((h, w), np.nan, dtype=np.float32)
                valide = (raw_pixels >= 0) & (raw_pixels <= 79)
                z_dbz[valide] = raw_pixels[valide] - 11
                
                data_2d = z_dbz
                break
                
        if data_2d is None:
            raise ValueError(f"Impossible de déterminer la taille de la grille mosaïque. Taille de l'array décodé: {len(arr)}")

        return MosaiqueRadar(
            nom_produit=nom_produit,
            maille_m=maille_m,
            data=data_2d,
            date_observation=decoded.get("datetime")
        )

    @classmethod
    def decode(cls, raw_bytes: bytes, format_attendu: str = None, nom_produit: str = "mosaique", maille_m: int = 1000) -> MosaiqueRadar:
        import gzip
        # Détection automatique du format par les Magic Bytes
        if raw_bytes.startswith(b'\x89HDF'):
            return cls.decode_hdf5(raw_bytes, nom_produit, maille_m)
        
        # Si c'est GZIP, on décompresse d'abord pour vérifier si c'est du HDF5 compressé ou du BUFR
        if raw_bytes.startswith(b'\x1f\x8b'):
            decompressed = gzip.decompress(raw_bytes)
            if decompressed.startswith(b'\x89HDF'):
                return cls.decode_hdf5(decompressed, nom_produit, maille_m)
            elif decompressed.startswith(b'BUFR'):
                return cls.decode_bufr(raw_bytes, nom_produit, maille_m) # On repasse raw_bytes car decode_bufr s'occupe de la décompression
                
        # Si c'est du LZW (.Z)
        if raw_bytes.startswith(b'\x1f\x9d'):
            return cls.decode_bufr(raw_bytes, nom_produit, maille_m)
            
        if raw_bytes.startswith(b'BUFR'):
            return cls.decode_bufr(raw_bytes, nom_produit, maille_m)

        # Fallback au format attendu si la détection automatique n'a rien donné
        if format_attendu and format_attendu.lower() in ("hdf", "hdf5"):
            return cls.decode_hdf5(raw_bytes, nom_produit, maille_m)
        else:
            return cls.decode_bufr(raw_bytes, nom_produit, maille_m)
