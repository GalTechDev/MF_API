import os
import eccodes
from typing import Dict, Any

# Chemin absolu vers les définitions eccodes générées
ECCODES_DEFS_DIR = os.path.join(os.path.dirname(__file__), "eccodes_defs")

# On s'assure qu'eccodes utilise bien nos définitions locales en priorité
# ECCODES_DEFINITION_PATH est de la forme: "chemin_local;chemin_systeme" (Windows utilise ';' et ':' sur unix)
sep = ';' if os.name == 'nt' else ':'
system_defs = os.path.join(os.path.dirname(eccodes.__file__), 'definitions')
os.environ['ECCODES_DEFINITION_PATH'] = f"{ECCODES_DEFS_DIR}{sep}{system_defs}"


class MFBufrDecoder:
    """
    Décodeur BUFR Météo-France utilisant eccodes.
    Ce décodeur gère nativement les tables locales de Météo-France
    générées dans le dossier eccodes_defs.
    """
    
    @staticmethod
    def decode(bufr_bytes: bytes) -> Dict[str, Any]:
        """
        Décode un message BUFR binaire et extrait les données en tant que dict.
        :param bufr_bytes: Les données binaires brutes du message BUFR (d'une trame)
        :return: Un dictionnaire contenant les valeurs extraites
        """
        # Eccodes a besoin d'un descripteur de fichier, on écrit temporairement sur le disque
        # (Ou alors on peut utiliser codes_bufr_new_from_message)
        # Bonne nouvelle : python-eccodes supporte grib_new_from_message / codes_new_from_message
        
        gid = eccodes.codes_new_from_message(bufr_bytes)
        try:
            # Ordre de désarchiver toutes les données (Section 4)
            eccodes.codes_set(gid, 'unpack', 1)
            
            # Extraction des données utiles
            data = {}
            # TODO: Implémenter l'extraction selon le type de message (PAM, PAG, etc.)
            
            # Exemple: extraction de la date de la section 1
            year = eccodes.codes_get(gid, "year")
            month = eccodes.codes_get(gid, "month")
            day = eccodes.codes_get(gid, "day")
            hour = eccodes.codes_get(gid, "hour")
            minute = eccodes.codes_get(gid, "minute")
            
            data["datetime"] = f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}"
            
            # Pour extraire les valeurs des descripteurs, par exemple les tableaux de données:
            # On peut utiliser codes_get_array
            # On stockera ici toutes les clefs "numericValues" qui contiennent la vraie donnée décompressée
            try:
                numeric_values = eccodes.codes_get_array(gid, "numericValues")
                data["numericValues"] = numeric_values.tolist()
            except Exception as e:
                # Certaines données BUFR pourraient ne pas avoir de 'numericValues' ou eccodes retourne une erreur
                data["numericValues"] = None
                
            return data
            
        finally:
            eccodes.codes_release(gid)

