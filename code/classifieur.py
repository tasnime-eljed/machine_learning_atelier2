
import json
import os
import time

from groq import Groq, RateLimitError

CATEGORIES = [
    "facturation",
    "technique",
    "compte",
    "commercial"
]

client = Groq(api_key=os.environ["GROQ_API_KEY"])

CONSIGNE = """
Tu es un agent de tri du service client.

Classe le ticket dans exactement une catégorie :
- facturation : montant, facture, paiement, remboursement.
- technique : un service ne fonctionne pas comme prévu.
- compte : accès au compte ou données personnelles.
- commercial : choix d'offre, abonnement, résiliation.

Si plusieurs catégories semblent possibles, retiens l'intention
principale du client : ce qu'il veut obtenir.

Réponds uniquement par un objet JSON de la forme :
{"categorie": "facturation"}
La valeur doit être l'une des quatre catégories autorisées.
"""

CONSIGNE_EXEMPLES = CONSIGNE + """
Exemples de classification :

"Le geste commercial promis n'est pas sur mon relevé."
-> {"categorie": "facturation"}

"Je paie chaque mois et rien ne marche depuis jeudi."
-> {"categorie": "technique"}

"Mon associé doit consulter les mêmes documents."
-> {"categorie": "compte"}

"Je déménage à l'étranger en septembre."
-> {"categorie": "commercial"}

Pour le nouveau ticket, applique les mêmes règles et réponds
uniquement avec un objet JSON contenant la catégorie.
"""



def classer(texte, modele, consigne=CONSIGNE, temperature=0.0):
    for tentative in range(4):
        try:
            reponse = client.chat.completions.create(
                model=modele,
                temperature=temperature,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": consigne},
                    {"role": "user", "content": texte}
                ]
            )

            contenu = reponse.choices[0].message.content

            try:
                donnees = json.loads(contenu)
                categorie = donnees.get("categorie", "")
            except (json.JSONDecodeError, AttributeError, TypeError):
                return "invalide"

            categorie = str(categorie).strip().lower()

            if categorie in CATEGORIES:
                return categorie

            return "invalide"

        except RateLimitError:
            if tentative == 3:
                raise
            time.sleep(5 * (tentative + 1))

    return "invalide"
