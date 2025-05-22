# Backend de l'application Watchbox

## Pour lancer l'application :

- Installer Python 3.13 : `brew install python@3.13`

- Créer le virtual env `python -m venv /path/to/new/virtual/environment`

- Activer le venv `source .venv/bin/activate` pour Mac / Linux ou `.venv\Scripts\activate` pour Windows

- Ajouter l'interpréteur du .venv sur Pycharm

- Installer les packages pip : `pip install -r requirements.txt`

- Lancer la commande `fastapi dev main.py`

## Pour lancer les tests :

- Installer pytest : `pip install -e .`

- lancer test : pytest -v
