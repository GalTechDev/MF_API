import os
import sys
import gzip
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from mf_api.decoders.eccodes_decoder import MFBufrDecoder

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
    
    os.makedirs(os.path.dirname(name), exist_ok=True)
    plt.savefig(f"{name}.png")
    plt.close()

def afficher_sigma(sigma_data, name):
    fig = plt.figure(figsize=(8, 7))
    plt.imshow(sigma_data, cmap='gray_r', origin='upper', extent=[-256, 256, -256, 256])
    plt.colorbar(label='Sigma (dB)')
    plt.title("Écart-type de réflectivité (Sigma)")
    
    os.makedirs(os.path.dirname(name), exist_ok=True)
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
    
    os.makedirs(os.path.dirname(name), exist_ok=True)
    plt.savefig(f"{name}_Adv.png")
    plt.close()

def separer_produits_bufr(data):
    marqueur = b'BUFR'
    positions = []
    start = 0
    while True:
        pos = data.find(marqueur, start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + 4
        
    segments = []
    for i in range(len(positions)):
        debut = positions[i]
        fin = positions[i+1] if i+1 < len(positions) else None
        segments.append(data[debut:fin])
    return segments

def get_pixel_array(segment, expected_size, shape):
    data = MFBufrDecoder.decode(segment)
    arr = np.array(data["numericValues"])
    
    # On récupère les X dernières valeurs qui correspondent à l'image
    raw_pixels = arr[-expected_size:]
    return raw_pixels.reshape(shape)

class RadarTourEccodes:
    def __init__(self, segments):
        self.Z = self.resolve_Z(segments[0]) if len(segments) > 0 else None
        self.Sigma = self.resolve_Sigma(segments[1]) if len(segments) > 1 else None
        self.Vrad = self.resolve_Vrad(segments[2]) if len(segments) > 2 else None

    def resolve_Z(self, raw):
        Z_array = get_pixel_array(raw, 720 * 256, (720, 256))
        z_dbz = np.full(Z_array.shape, np.nan, dtype=np.float32)
        valide = (Z_array >= 0) & (Z_array <= 79)
        z_dbz[valide] = Z_array[valide] - 11
        return z_dbz

    def resolve_Sigma(self, raw):
        Sigma_array = get_pixel_array(raw, 360 * 256, (360, 256))
        Sigma_dB = np.full(Sigma_array.shape, np.nan, dtype=np.float32)
        valide = (Sigma_array >= 0) & (Sigma_array <= 63)
        Sigma_dB[valide] = Sigma_array[valide] * 0.25
        return Sigma_dB

    def resolve_Vrad(self, raw):
        Vrad_array = get_pixel_array(raw, 360 * 256, (360, 256))
        Vrad = np.full(Vrad_array.shape, np.nan, dtype=np.float32)
        valide = (Vrad_array >= 0) & (Vrad_array <= 241)
        Vrad[valide] = (Vrad_array[valide] * 0.5) - 60.25
        return Vrad

class RadarTourBiEccodes:
    def __init__(self, segments):
        self.ZH = self.resolve_ZH(segments[0]) if len(segments) > 0 else None
        self.rhoHV = self.resolve_rhoHV(segments[1]) if len(segments) > 1 else None
        self.PhiDP = self.resolve_PhiDP(segments[2]) if len(segments) > 2 else None
        self.ZDR = self.resolve_ZDR(segments[3]) if len(segments) > 3 else None
        self.Sigma = self.resolve_Sigma(segments[4]) if len(segments) > 4 else None
        self.Adv = self.resolve_Adv(segments[5]) if len(segments) > 5 else None

    def resolve_ZH(self, raw):
        ZH_array = get_pixel_array(raw, 720 * 1066, (720, 1066))
        zh_dbz = np.full(ZH_array.shape, np.nan, dtype=np.float32)
        valide = (ZH_array >= 0) & (ZH_array <= 79)
        zh_dbz[valide] = ZH_array[valide] - 11
        return zh_dbz

    def resolve_rhoHV(self, raw):
        rhoHV_array = get_pixel_array(raw, 720 * 1066, (720, 1066))
        rhoHV_coef = np.full(rhoHV_array.shape, np.nan, dtype=np.float32)
        valide = (rhoHV_array >= 0) & (rhoHV_array <= 79)
        rhoHV_coef[valide] = (rhoHV_array[valide] / 100.0) + 0.3
        return rhoHV_coef

    def resolve_PhiDP(self, raw):
        PhiDP_array = get_pixel_array(raw, 720 * 1066, (720, 1066))
        PhiDP_deg = np.full(PhiDP_array.shape, np.nan, dtype=np.float32)
        valide = (PhiDP_array >= 0) & (PhiDP_array <= 359)
        PhiDP_deg[valide] = PhiDP_array[valide]
        return PhiDP_deg

    def resolve_ZDR(self, raw):
        ZDR_array = get_pixel_array(raw, 720 * 1066, (720, 1066))
        ZDR_deg = np.full(ZDR_array.shape, np.nan, dtype=np.float32)
        valide = (ZDR_array >= 0) & (ZDR_array <= 199)
        ZDR_deg[valide] = (ZDR_array[valide] / 10.0) - 10.0
        return ZDR_deg

    def resolve_Sigma(self, raw):
        Sigma_array = get_pixel_array(raw, 512 * 512, (512, 512))
        Sigma_dB = np.full(Sigma_array.shape, np.nan, dtype=np.float32)
        valide = (Sigma_array >= 0) & (Sigma_array <= 63)
        Sigma_dB[valide] = Sigma_array[valide] * 0.25
        return Sigma_dB

    def resolve_Adv(self, raw):
        adv_raw = get_pixel_array(raw, 16 * 16 * 2 * 2, (16, 16, 4))
        # Wait, the Adv is 16x16 with 2 bytes per component, meaning 16*16*4 values.
        # It's better to just use raw values like before
        # But eccodes gives us numbers directly! Advection components might be decoded correctly!
        # For advection, test.py.old used np.frombuffer(section4, dtype=np.uint16)
        # eccodes numericValues will contain the values. 
        # But to be safe, we fall back to the binary method for advection.
        data_size = 16 * 16 * 4
        fin_section = raw.find(b'7777')
        section4 = raw[fin_section - data_size : fin_section]
        adv_raw_bin = np.frombuffer(section4, dtype=np.uint16)
        vx = adv_raw_bin[0::2]
        vy = adv_raw_bin[1::2]
        
        def convertir(code):
            res = (code.astype(float) / 100.0) - 327.68
            res[code == 65534] = np.nan
            return res

        vx_ms = convertir(vx).reshape((16, 16))
        vy_ms = convertir(vy).reshape((16, 16))
        
        return vx_ms, vy_ms

def loadRadarcycle(FILE, fichier):
    path = os.path.join(FILE, fichier)
    print(f"Loading {path} with eccodes_decoder...")
    with gzip.open(path, 'rb') as f_in:
        try:
            data = f_in.read()
        except gzip.BadGzipFile:
            print(f"Error decoding {fichier}")
            return

        segments = separer_produits_bufr(data)
        print(f"Nombre de produits trouvés dans {fichier}: {len(segments)}")

        img_dir = f"img_eccodes/{fichier[:-8]}"
        os.makedirs(img_dir, exist_ok=True)

        if fichier.startswith("T_PAM") and len(segments) == 6:
            try:
                product = RadarTourBiEccodes(segments)
            except Exception as e:
                print(e)
                return
            
            afficher_radar_polaire(product.ZH, f"{img_dir}/ZH_{fichier[:-8]}", "dBZ", vmin=-10, vmax=60, azimuts_range=720)
            afficher_radar_polaire(product.rhoHV, f"{img_dir}/rhoHV_{fichier[:-8]}", "rhoHV", cmap='viridis', vmin=0.8, vmax=1.0, azimuts_range=720)
            afficher_radar_polaire(product.PhiDP, f"{img_dir}/PhiDP_{fichier[:-8]}", "Degrés", cmap='twilight', azimuts_range=720)
            afficher_radar_polaire(product.ZDR, f"{img_dir}/ZDR_{fichier[:-8]}", "dB", cmap='coolwarm', vmin=-2, vmax=4, azimuts_range=720)
            afficher_sigma(product.Sigma, f"{img_dir}/Sigma_{fichier[:-8]}")
            vx, vy = product.Adv
            afficher_advection(vx, vy, f"{img_dir}/Adv_{fichier[:-8]}")

        if fichier.startswith("T_PAG") and len(segments) == 3:
            try:
                product = RadarTourEccodes(segments)
            except Exception as e:
                print(e)
                return
            
            afficher_radar_polaire(product.Z, f"{img_dir}/Z_{fichier[:-8]}", "dBZ", vmin=-10, vmax=60, azimuts_range=720, nb_portes=256)
            afficher_radar_polaire(product.Sigma, f"{img_dir}/Sigma_{fichier[:-8]}", "dB", nb_portes=256)
            afficher_radar_polaire(product.Vrad, f"{img_dir}/V_rad_{fichier[:-8]}", "m/s", nb_portes=256)


if __name__ == "__main__":
    FILE_DIR = os.path.join(os.path.dirname(__file__), "..", "bufr", "data", "paquetradar_station_96_20260604224500")
    for fichier in os.listdir(FILE_DIR):
        if fichier.endswith(".bufr.gz"):
            loadRadarcycle(FILE_DIR, fichier)

