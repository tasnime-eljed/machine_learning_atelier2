# Machine learning appliqué · 3e année DSI
## Atelier 2 — Choisir un modèle sur preuves

---

### Tableau de synthèse de décision

| Rubrique | À remplir |
| :--- | :--- |
| **Tâche et jeu de test** | **Router les tickets vers quatre équipes ; 72 tickets annotés, classes déséquilibrées**<br>• *Jeu de données* : `data/tickets.csv` (72 tickets annotés en 4 catégories).<br>• *Répartition des classes* : facturation (22, soit 30.6%), technique (20, soit 27.8%), compte (16, soit 22.2%), commercial (14, soit 19.4%). |
| **Métrique de décision** | **macro-F1, choisie avant de voir les résultats**<br>• Permet d'accorder le même poids à chaque catégorie indépendamment de son effectif dans le jeu de test.<br>• Évite de masquer les mauvaises performances sur les classes minoritaires (ex. *commercial*). |
| **Candidats évalués** | Quatre configurations testées via l'API Groq :<br>1. **`qwen/qwen3.8-27b`** (zero-shot, consigne standard) : **macro-F1 = 0.956** (Acc = 95.83%, 69/72)<br>2. **`qwen/qwen3.8-27b + 4 exemples`** (few-shot, consigne enrichie) : **macro-F1 = 0.956** (Acc = 95.83%, 69/72)<br>3. **`openai/gpt-oss-20b`** (zero-shot, consigne standard) : **macro-F1 = 0.929** (Acc = 93.06%, 67/72)<br>4. **`openai/gpt-oss-120b`** (zero-shot, consigne standard) : **macro-F1 = 0.915** (Acc = 91.67%, 66/72) |
| **Modèle retenu et son score** | **Modèle retenu : `qwen/qwen3.8-27b`** (version standard zero-shot)<br>• **Score macro-F1 : 0.956** (0.9559)<br>• **Accuracy : 95.83%** (69 tickets corrects sur 72, seulement 3 erreurs)<br>• **Taux d'invalides : 0.00%** (100% de sorties JSON valides)<br>• *Justification* : À score macro-F1 identique à la version avec exemples (0.956), la version zero-shot offre une latence plus faible (193.8 s vs 212.7 s) et consomme moins de tokens. |
| **Écart avec le deuxième** | **En points ET en nombre de tickets** :<br>• **En points de macro-F1** : **+2.7 points** (+0.0273) par rapport à `openai/gpt-oss-20b` (0.956 vs 0.929). *(+4.1 points par rapport à `openai/gpt-oss-120b`)*.<br>• **En points d'Accuracy** : **+2.78 points** (95.83% vs 93.06%).<br>• **En nombre de tickets** : **+2 tickets** correctement classés en plus (69/72 pour Qwen contre 67/72 pour GPT-OSS-20B, soit 3 erreurs vs 5 erreurs). |
| **Catégorie la plus faible, latence, risque identifié** | • **Catégorie la plus faible** : **`commercial`** avec un score **F1 de 0.923** (Rappel de 85.7%, 12/14 bien classés, 2 tickets orientés à tort vers la facturation).<br>• **Latence moyenne** : **~0.62 s par requête** (durée brute d'inférence API ~44.7 s pour 72 requêtes hors pause technique de 2.1 s ; durée totale observée 193.8 s). C'est le modèle le plus rapide.<br>• **Risque identifié** : Confusion entre réclamation commerciale et facturation (tickets parlant de prix/montants comme T004 *"Je paie 40 euros pour un service que j'utilise deux fois par mois"*). Risque d'orienter un client insatisfait souhaitant résilier/changer d'offre vers la facturation au lieu d'un conseiller commercial (risque d'attrition/churn). |

---

### Annexe 1 : Résultats détaillés des 4 candidats

| Modèle | Accuracy | Macro-F1 | Invalides | Durée totale | Latence nette / req | Facturation (F1) | Technique (F1) | Compte (F1) | Commercial (F1) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **qwen/qwen3.8-27b** *(Retenu)* | **95.8 %** (69/72) | **0.956** | **0.0 %** | **193.8 s** | **~0.62 s** | 0.957 | 0.974 | 0.970 | 0.923 |
| **qwen/qwen3.8-27b (+ 4 ex.)** | **95.8 %** (69/72) | **0.956** | **0.0 %** | 212.7 s | ~0.88 s | 0.978 | 0.947 | 0.970 | 0.929 |
| **openai/gpt-oss-20b** | 93.1 % (67/72) | 0.929 | 0.0 % | 223.7 s | ~1.04 s | 0.930 | 0.950 | 0.938 | 0.897 |
| **openai/gpt-oss-120b** | 91.7 % (66/72) | 0.915 | 0.0 % | 224.3 s | ~1.04 s | 0.913 | 0.919 | 0.970 | 0.857 |

---

### Annexe 2 : Analyse des erreurs du modèle retenu (`qwen/qwen3.8-27b`)

Sur les 72 tickets du jeu de test, le modèle retenu n'a commis que 3 erreurs :

1. **Ticket T004** *(ambigu = 1)* :
   - *Texte* : `"Je paie 40 euros pour un service que j'utilise deux fois par mois."`
   - *Vérité terrain* : `commercial` | *Prédiction* : `facturation`
   - *Explication* : Mention explicite d'une somme (`40 euros`) qui attire le modèle vers `facturation`, alors que l'intention sous-jacente est l'adéquation de l'offre (commercial).

2. **Ticket T040** *(ambigu = 1)* :
   - *Texte* : `"mon voisin paye moins cher que moi pour la meme chose"`
   - *Vérité terrain* : `commercial` | *Prédiction* : `facturation`
   - *Explication* : Comparaison tarifaire perçue comme un problème de montant facturé au lieu d'une renégociation commerciale d'offre.

3. **Ticket T041** *(ambigu = 0)* :
   - *Texte* : `"mon espace client saffiche pas"`
   - *Vérité terrain* : `technique` | *Prédiction* : `compte`
   - *Explication* : L'expression *"espace client"* a orienté le modèle vers `compte`, bien qu'il s'agisse d'un dysfonctionnement d'affichage (technique).
