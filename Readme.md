# CCO Nexus Scipt
## _Script d'export Nexus_

 [![PyPI - Python](https://img.shields.io/pypi/pyversions/iconsdk?logo=pypi)](https://pypi.org/project/iconsdk)

## Description
Dans le cadre du projet Replicant, tous les exports de référentiels VTOM (BSCC) sont envoyés sur Nexus BSCC dans le dépôt raw-cco-export. Ce script permet de réaliser les tâches suivantes:

>  [nexusSelenium.py](https://github.gsissc.myatos.net/A823921/CCO-Nexus/blob/main/nexusSelenium.py) remplacé par [nexusAPI.py](https://github.gsissc.myatos.net/A823921/CCO-Nexus/blob/main/nexusAPI.py)

- ~~Se connecter à Nexus~~
- ~~Authentification 1~~
- ~~Authentification 2 (sur Nexus)~~
- ~~Naviger vers le repo raw-cco-export~~
- ~~Télécharger tous les fichiers (archives *.tgz)~~
- ~~Extraire les fichiers dans un dossier donné~~

- Se connecte a Nexus Repo via REST API
- Cherche un repo donné
- Télécharge tous les archives dans un dossier de sortie




## Installation

Ce script necessite: 
- [Python 2.7.18](https://www.python.org/downloads/release/python-2718/) 
- [pip 20.3.4](https://pypi.org/project/pip/) 

Installez les modules:

```sh
# cloner le repo
git clone https://github.gsissc.myatos.net/A823921/CCO-Nexus.git && cd CCO-Nexus
# Installation de modules pip
pip install -r .\requirements.txt
# Ou
python -m pip install -r .\requirements.txt
```

