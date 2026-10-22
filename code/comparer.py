
import json
from pathlib import Path
from itertools import combinations

BASE_DIR = Path(__file__).resolve().parent.parent
DOSSIER_RESULTATS = BASE_DIR / "resultats"


def charger_resultats():
    resultats = []

    for chemin in sorted(DOSSIER_RESULTATS.glob("*.json")):
        try:
            with open(chemin, encoding="utf-8") as fichier:
                donnees = json.load(fichier)

            # Ne garder que les fichiers contenant les prédictions
            if "predits" in donnees and "ids" in donnees:
                resultats.append(donnees)

        except (json.JSONDecodeError, OSError) as erreur:
            print(f"Fichier ignoré : {chemin.name} ({erreur})")

    return resultats


def comparer():
    resultats = charger_resultats()

    if len(resultats) < 2:
        print("Il faut au moins deux évaluations enregistrées.")
        print("Lancez evaluer.py pour les modèles à comparer.")
        return

    print("\n=== TABLEAU COMPARATIF ===")
    print(
        f"{'Modèle':<28}"
        f"{'Accuracy':>10}"
        f"{'Macro-F1':>11}"
        f"{'Invalides':>11}"
        f"{'Durée (s)':>12}"
    )

    for r in sorted(
        resultats,
        key=lambda x: x.get("macro_f1", 0),
        reverse=True
    ):
        print(
            f"{r.get('modele', r.get('etiquette', '?')):<28}"
            f"{r.get('accuracy', 0):>10.3f}"
            f"{r.get('macro_f1', 0):>11.3f}"
            f"{r.get('invalides', 0):>11.3f}"
            f"{r.get('duree_s', 0):>12.1f}"
        )

    print("\n=== DÉSACCORDS ENTRE MODÈLES ===")

    for a, b in combinations(resultats, 2):
        pred_a = dict(zip(a["ids"], a["predits"]))
        pred_b = dict(zip(b["ids"], b["predits"]))

        ids_communs = sorted(set(pred_a) & set(pred_b))
        divergences = [
            identifiant for identifiant in ids_communs
            if pred_a[identifiant] != pred_b[identifiant]
        ]

        print(
            f"\n{a.get('modele', a.get('etiquette'))} "
            f"vs {b.get('modele', b.get('etiquette'))}"
        )
        print(
            f"Désaccords : {len(divergences)} "
            f"sur {len(ids_communs)} tickets communs"
        )

        for identifiant in divergences:
            print(
                f"  Ticket {identifiant} : "
                f"{pred_a[identifiant]} / {pred_b[identifiant]}"
            )

    # Tickets sur lesquels tous les modèles ne sont pas d'accord
    tous = resultats
    if len(tous) >= 3:
        predictions = [
            dict(zip(r["ids"], r["predits"])) for r in tous
        ]
        ids_communs = set(predictions[0])

        for p in predictions[1:]:
            ids_communs &= set(p)

        desaccords_tous = [
            identifiant for identifiant in sorted(ids_communs)
            if len({p[identifiant] for p in predictions}) > 1
        ]

        print("\n=== TICKETS OÙ LES MODÈLES NE SONT PAS UNANIMES ===")
        print(f"Nombre de tickets concernés : {len(desaccords_tous)}")

        for identifiant in desaccords_tous:
            details = [
                f"{r.get('modele', r.get('etiquette'))}="
                f"{p[identifiant]}"
                for r, p in zip(tous, predictions)
            ]
            print(f"Ticket {identifiant} : " + " | ".join(details))


if __name__ == "__main__":
    comparer()
