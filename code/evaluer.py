
import csv
import json
import sys
import time
from pathlib import Path

from classifieur import CONSIGNE, classer
from evaluation import afficher_rapport


# Chemins des fichiers
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "tickets.csv"
RESULTATS_DIR = BASE_DIR / "resultats"

# Pause pour respecter la limite de requêtes de l'API
PAUSE = 2.1


def charger_tickets():
    with open(DATA_FILE, encoding="utf-8", newline="") as fichier:
        return list(csv.DictReader(fichier))


def evaluer(modele, lignes, consigne=CONSIGNE, etiquette=None):
    etiquette = etiquette or modele

    vrais = []
    predits = []
    debut = time.time()

    for i, ligne in enumerate(lignes, start=1):
        vrai = ligne["categorie"].strip().lower()
        predit = classer(
            ligne["texte"],
            modele,
            consigne=consigne
        )

        vrais.append(vrai)
        predits.append(predit)

        print(
            f"[{i}/{len(lignes)}] "
            f"Ticket {ligne['id']} : {predit}"
        )

        if i < len(lignes):
            time.sleep(PAUSE)

    # Calcul et affichage des indicateurs
    resume = afficher_rapport(etiquette, vrais, predits)

    # Ajouter des informations utiles au rapport
    resume.update({
        "modele": modele,
        "etiquette": etiquette,
        "duree_s": round(time.time() - debut, 1),
        "predits": predits,
        "ids": [ligne["id"] for ligne in lignes]
    })

    # Créer le dossier de résultats s'il n'existe pas
    RESULTATS_DIR.mkdir(parents=True, exist_ok=True)

    nom_fichier = (
    etiquette.replace("/", "_")
    .replace("\\", "_")
    .replace(" ", "_")
)
    chemin_sortie = RESULTATS_DIR / f"{nom_fichier}.json"

    with open(chemin_sortie, "w", encoding="utf-8") as fichier:
        json.dump(resume, fichier, ensure_ascii=False, indent=2)

    print(f"\nRésultats enregistrés dans : {chemin_sortie}")

    return resume


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python .\\code\\evaluer.py <nom_du_modele>")
        sys.exit(1)

    modele = sys.argv[1]
    tickets = charger_tickets()

    print(f"Nombre de tickets : {len(tickets)}")
    print(f"Modèle testé : {modele}")

    evaluer(modele, tickets)
