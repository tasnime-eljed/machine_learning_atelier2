
from classifieur import CONSIGNE_EXEMPLES
from evaluer import charger_tickets, evaluer

MODELE = "qwen/qwen3.8-27b"

if __name__ == "__main__":
    tickets = charger_tickets()

    evaluer(
        MODELE,
        tickets,
        consigne=CONSIGNE_EXEMPLES,
        etiquette=MODELE + " + 4 exemples"
    )
