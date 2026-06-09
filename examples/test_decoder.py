import os
import sys
import gzip
import tarfile
import numpy as np
import matplotlib.pyplot as plt

# Ajoute le dossier parent au chemin d'importation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mf_api.decoders import decode_mf_bufr

# ==========================================
# Fonctions d'affichage (issues de l'ancien code)
# ==========================================
def afficher_radar_polaire(data, name, label, cmap='nipy_spectral', vmin=None, vmax=None, azimuts_range=360, nb_portes=1066):
    azimuts = np.linspace(0, 360, azimuts_range)
    portes = np.arange(nb_portes) * 0.240
    az, dist = np.meshgrid(np.radians(azimuts), portes)

    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_subplot(111, projection='polar')
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)

    mesh = ax.pcolormesh(az, dist, data.T, cmap=cmap, vmin=vmin, vmax=vmax)
    plt.colorbar(mesh, label=label)
    plt.savefig(f"{name}.png")
    plt.close()

def afficher_sigma(sigma_data, name):
    fig = plt.figure(figsize=(8, 7))
    plt.imshow(sigma_data, cmap='gray_r', origin='upper', extent=[-256, 256, -256, 256])
    plt.colorbar(label='Sigma (dB)')
    plt.title("Écart-type de réflectivité (Sigma)")
    plt.savefig(f"{name}_Sigma.png")
    plt.close()

def afficher_advection(vx, vy, name):
    fig = plt.figure(figsize=(8, 8))
    x = np.linspace(-256, 256, 16)
    y = np.linspace(256, -256, 16)
    X, Y = np.meshgrid(x, y)
    
    plt.quiver(X, Y, vx, -vy, color='blue')
    plt.title("Vecteurs d'Advection")
    plt.grid(True)
    plt.savefig(f"{name}_Adv.png")
    plt.close()

# ==========================================
# Fallback Extraction (en l'absence des tables locales pybufrkit)
# ==========================================
class RadarTourFallback:
    """Fallback pour décoder PAM/PAG directement depuis les octets d'un message."""
    
    @staticmethod
    def extract_array(raw, shape, formula_func, dtype=np.uint8):
        data_size = shape[0] * shape[1] * (2 if dtype==np.uint16 else 1)
        # La nouvelle séparation BUFR s'assure que 7777 est à la fin du segment
        fin_section = raw.rfind(b'7777')
        if fin_section == -1: return None
        
        section4 = raw[fin_section - data_size : fin_section]
        if len(section4) != data_size: return None
        
        arr = np.frombuffer(section4, dtype=dtype).reshape(shape)
        return formula_func(arr)

    @staticmethod
    def extract_ZH(raw):
        def calc(arr):
            res = np.full(arr.shape, np.nan, dtype=np.float32)
            valide = (arr >= 0) & (arr <= 79)
            res[valide] = arr[valide] - 11
            return res
        return RadarTourFallback.extract_array(raw, (720, 1066), calc)

    @staticmethod
    def extract_Z(raw):
        def calc(arr):
            res = np.full(arr.shape, np.nan, dtype=np.float32)
            valide = (arr >= 0) & (arr <= 79)
            res[valide] = arr[valide] - 11
            return res
        return RadarTourFallback.extract_array(raw, (720, 256), calc)

    @staticmethod
    def extract_rhoHV(raw):
        def calc(arr):
            res = np.full(arr.shape, np.nan, dtype=np.float32)
            valide = (arr >= 0) & (arr <= 79)
            res[valide] = (arr[valide] / 100.0) + 0.3
            return res
        return RadarTourFallback.extract_array(raw, (720, 1066), calc)

    @staticmethod
    def extract_ZDR(raw):
        def calc(arr):
            res = np.full(arr.shape, np.nan, dtype=np.float32)
            valide = (arr >= 0) & (arr <= 199)
            res[valide] = (arr[valide] / 10.0) - 10.0
            return res
        return RadarTourFallback.extract_array(raw, (720, 1066), calc)


# ==========================================
# Programme Principal
# ==========================================
def run_example():
    DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "bufr", "data", "paquetradar_station_96_20260604224500")
    IMG_DIR = os.path.join(os.path.dirname(__file__), "..", "img")
    
    if not os.path.exists(IMG_DIR):
        os.makedirs(IMG_DIR)

    if not os.path.exists(DATA_DIR):
        print(f"Dossier de données introuvable : {DATA_DIR}")
        return

    for fichier in os.listdir(DATA_DIR):
        if not fichier.endswith(".bufr.gz"):
            continue
            
        print(f"\nTraitement de {fichier}...")
        filepath = os.path.join(DATA_DIR, fichier)
        
        try:
            with gzip.open(filepath, 'rb') as f_in:
                data = f_in.read()
        except gzip.BadGzipFile:
            print(f"Erreur GZIP pour {fichier}")
            continue
            
        # Utilisation du nouveau décodeur pour segmenter et parser proprement
        decoded_messages = decode_mf_bufr(data, return_type="numpy")
        print(f"Nombre de messages BUFR trouvés : {len(decoded_messages)}")
        
        img_sub_dir = os.path.join(IMG_DIR, fichier[:-8])
        if not os.path.exists(img_sub_dir):
            os.makedirs(img_sub_dir)

        # Si le fichier est un T_PAM (généralement 6 messages : ZH, rhoHV, PhiDP, ZDR, Sigma, Adv)
        if fichier.startswith("T_PAM") and len(decoded_messages) >= 4:
            # En l'absence de tables locales compilées, pybufrkit renvoie une erreur sur la section 4.
            # On utilise donc le "raw_bytes" garanti par le décodeur pour extraire les tableaux.
            
            zh_msg = decoded_messages[0]["raw_bytes"]
            rho_msg = decoded_messages[1]["raw_bytes"]
            zdr_msg = decoded_messages[3]["raw_bytes"]
            
            ZH = RadarTourFallback.extract_ZH(zh_msg)
            rhoHV = RadarTourFallback.extract_rhoHV(rho_msg)
            ZDR = RadarTourFallback.extract_ZDR(zdr_msg)
            
            if ZH is not None:
                afficher_radar_polaire(ZH, f"{img_sub_dir}/ZH_{fichier[:-8]}", "dBZ", vmin=-10, vmax=60, azimuts_range=720)
                print(" -> ZH généré")
            if rhoHV is not None:
                afficher_radar_polaire(rhoHV, f"{img_sub_dir}/rhoHV_{fichier[:-8]}", "rhoHV", cmap='viridis', vmin=0.8, vmax=1.0, azimuts_range=720)
                print(" -> rhoHV généré")
            if ZDR is not None:
                afficher_radar_polaire(ZDR, f"{img_sub_dir}/ZDR_{fichier[:-8]}", "dB", cmap='coolwarm', vmin=-2, vmax=4, azimuts_range=720)
                print(" -> ZDR généré")

if __name__ == "__main__":
    run_example()
