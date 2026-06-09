# MF API (Météo-France API Wrapper)

## IN PROGRESS
Cette librairie n'est pas encore finalisé et des bugs peuvent être présent ou fonctionnalitées manquantes.

## Decsription

`mf-api` est un wrapper Python non officiel pour interroger les APIs publiques de Météo-France.
Le wrapper se décompose en 2 parties : 

- `mf-api.api` pour intéroger les APIs de Météo-France
- `mf-api.decoders` pour serialiser les données en Class python pour les produits complexe comme les produits radar ou de prévision

## Installation

Vous pouvez installer la librairie localement :

```bash
pip install mf-api
```

Si vous souhaitez décoder les données de radars météorologiques (BUFR, HDF5, LZW, GZIP), installez les dépendances optionnelles :

```bash
pip install "mf-api[radar]"
```

## Fonctionnalités

- Authentification automatique (via `.env` et token Météo-France)
- Wrapper pour l'API publique de Météo France (https://portail-api.meteofrance.fr)
- Décodage des formats radar complexes (BUFR compressés, données polaires `eccodes`)

## Prochainement

- Décodage pour les produits de prévisions
- Résolution de bug
- Renforcement de l'architecture