# MF API (Météo-France API Wrapper)

`mf-api` est un wrapper Python non officiel pour interroger les APIs publiques de Météo-France.

## Installation

Vous pouvez installer la librairie localement :

```bash
pip install -e .
```

Si vous souhaitez décoder les données de radars météorologiques (BUFR, HDF5, LZW, GZIP), installez les dépendances optionnelles :

```bash
pip install -e ".[radar]"
```

## Fonctionnalités

- Authentification automatique (via `.env` et token Météo-France)
- Mosaïques radar (Métropole et Outre-mer)
- Données des stations radar individuelles
- Décodage natif des formats complexes (BUFR compressés, données polaires `eccodes`)

## Documentation

- [Traitement des données Radar](docs/radar_processing.md)
