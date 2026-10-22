CATEGORIES = ["facturation", "technique", "compte", "commercial"]


def accuracy(vrais, predits):
    if not vrais:
        return 0.0

    return sum(
        1 for v, p in zip(vrais, predits) if v == p
    ) / len(vrais)


def scores_par_classe(vrais, predits, classes=CATEGORIES):
    resultat = {}

    for c in classes:
        vp = sum(1 for v, p in zip(vrais, predits) if v == c and p == c)
        fp = sum(1 for v, p in zip(vrais, predits) if v != c and p == c)
        fn = sum(1 for v, p in zip(vrais, predits) if v == c and p != c)

        precision = vp / (vp + fp) if (vp + fp) else 0.0
        recall = vp / (vp + fn) if (vp + fn) else 0.0

        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall)
            else 0.0
        )

        resultat[c] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": sum(1 for v in vrais if v == c)
        }

    return resultat


def f1_macro(scores):
    if not scores:
        return 0.0

    return sum(d["f1"] for d in scores.values()) / len(scores)


def taux_invalides(predits):
    if not predits:
        return 0.0

    return sum(1 for p in predits if p == "invalide") / len(predits)


def matrice_confusion(vrais, predits):
    colonnes = CATEGORIES + ["invalide"]

    matrice = {
        c: {p: 0 for p in colonnes}
        for c in CATEGORIES
    }

    for vrai, predit in zip(vrais, predits):
        if vrai in CATEGORIES:
            colonne = predit if predit in CATEGORIES else "invalide"
            matrice[vrai][colonne] += 1

    return matrice


def afficher_rapport(etiquette, vrais, predits):
    scores = scores_par_classe(vrais, predits)
    macro = f1_macro(scores)
    acc = accuracy(vrais, predits)
    invalides = taux_invalides(predits)
    matrice = matrice_confusion(vrais, predits)

    print(f"\n=== {etiquette} ===")
    print(f"accuracy    : {acc:.3f}")
    print(f"macro-F1    : {macro:.3f}")
    print(f"invalides   : {invalides:.3f}")

    print(
        f"\n{'categorie':<15}{'precision':>11}"
        f"{'recall':>10}{'F1':>10}{'n':>7}"
    )

    for c, s in scores.items():
        print(
            f"{c:<15}{s['precision']:>11.3f}"
            f"{s['recall']:>10.3f}{s['f1']:>10.3f}"
            f"{s['support']:>7}"
        )

    colonnes = CATEGORIES + ["invalide"]
    print("\nMatrice de confusion (lignes = vérité, colonnes = prédiction)")
    print(f"{'':<15}" + "".join(f"{p:>13}" for p in colonnes))

    for c, valeurs in matrice.items():
        print(f"{c:<15}" + "".join(f"{valeurs[p]:>13}" for p in colonnes))

    return {
        "accuracy": acc,
        "macro_f1": macro,
        "invalides": invalides,
        "scores": scores,
        "matrice_confusion": matrice
    }
