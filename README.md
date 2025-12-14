#  Service de Recherche Sémantique

Un puissant **service de recherche sémantique basé sur FastAPI** pour les repas, utilisant l'indexation **FAISS** (Facebook AI Similarity Search) et **Sentence Transformers** pour la génération d'embeddings.

---

##  Table des Matières

- [Aperçu](#aperçu)
- [Structure du Projet](#structure-du-projet)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Construction de l'Index](#construction-de-lindex)
- [Lancement de l'API](#lancement-de-lapi)
- [Test de l'API](#test-de-lapi)
- [Documentation de l'API](#documentation-de-lapi)

---

##  Aperçu

Ce service permet la **recherche sémantique** à travers les documents de repas. Contrairement à la recherche traditionnelle par mots-clés, la recherche sémantique comprend le **sens** et le **contexte** de vos requêtes, retournant des résultats pertinents même lorsque les mots-clés exacts ne correspondent pas.

### Fonctionnalités Clés

-  Recherche par similarité sémantique utilisant les embeddings de phrases
-  Recherche rapide de similarité vectorielle avec l'indexation FAISS
-  API RESTful avec FastAPI
-  Retourne les détails des repas avec des scores de pertinence

---

##  Structure du Projet

```
semantic-search-service/
├── main.py                 # Point d'entrée de l'application FastAPI
├── requirements.txt        # Dépendances Python
├── README.md              # Ce fichier
│
├── Documents/             #  Documents de repas et fichiers d'index
│   ├── meals.index        # Fichier d'index FAISS pour la recherche rapide
│   ├── meal_ids.json      # Correspondance entre positions d'index et IDs de repas
│   └── meal_*.docx        # Documents individuels de repas (format DOCX)
│
├── models/                #  Modèles de données
│   ├── __init__.py
│   └── meal.py            # Modèle de données repas (MealRequest)
│
├── routers/               #  Routes API
│   ├── __init__.py
│   └── meals.py           # Endpoints de recherche de repas
│
├── services/              #  Logique métier
│   ├── __init__.py
│   ├── build_index.py     # Script pour construire l'index FAISS
│   └── search_service.py  # Implémentation du service de recherche
│
└── test/                  # Fichiers de test et documents exemples
    └── *.docx             # Documents de repas de test
```

###  Dossier Documents

Le dossier `/Documents` est le **répertoire de données principal** contenant :

| Fichier | Description |
|---------|-------------|
| `meals.index` | Index FAISS qui va contenir les embeddings vectoriels de tous les documents de repas. Cela permet une recherche de similarité rapide. |
| `meal_ids.json` | Fichier JSON faisant la correspondance entre les positions d'index FAISS et les UUIDs réels des repas. |
| `meal_*.docx` | Fichiers de documents de repas individuels au format DOCX, chacun contenant des informations détaillées sur le repas (nom, ingrédients, nutrition, etc.). |

---

##  Prérequis

- **Python 3.10+**
- **pip** (gestionnaire de paquets Python)

---

##  Installation

1. **Cloner le dépôt** (si ce n'est pas déjà fait)

2. **Installer les dépendances requises :**

```bash
pip install -r requirements.txt
```

Cela installera :
- `fastapi` - Framework web
- `uvicorn` - Serveur ASGI
- `sentence-transformers` - Pour générer les embeddings de texte
- `faiss-cpu` - Pour la recherche de similarité vectorielle
- `python-docx` - Pour lire les fichiers DOCX

---

##  Construction de l'Index

Avant de lancer l'API, vous devez construire l'index FAISS à partir des documents de repas.

### Étape 1 : Naviguer vers le dossier services

```bash
cd services
```

### Étape 2 : Exécuter le script de construction d'index

```bash
python build_index.py
```

### Que se passe-t-il pendant l'indexation ?

1.  Lecture de tous les fichiers `.docx` du dossier `/Documents`
2.  Extraction du contenu textuel de chaque document
3.  Génération des embeddings sémantiques avec Sentence Transformers
4.  Sauvegarde de l'index FAISS dans `Documents/meals.index`
5.  Création de `Documents/meal_ids.json` pour la correspondance des IDs

---

##  Lancement de l'API

### Étape 1 : Retourner au dossier racine

```bash
cd ..
```

### Étape 2 : Démarrer le serveur FastAPI

```bash
uvicorn main:app --reload
```

Le serveur démarrera à l'adresse : **http://localhost:8000**

>  L'option `--reload` active le rechargement automatique pendant le développement.

---

##  Test de l'API

### Avec Postman, cURL ou un Navigateur

Envoyez une requête **GET** vers l'endpoint de recherche :

```
GET http://localhost:8000/meals/search?query=chicken&top_k=5
```

### Paramètres de Requête

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `query` | string | Oui | Le texte de recherche (ex: "poulet", "pâtes", "petit-déjeuner sain") |
| `top_k` | integer | Non | Nombre de résultats à retourner (par défaut : 5) |

### Exemple de Requête

```bash
curl "http://localhost:8000/meals/search?query=healthy%20soup&top_k=3"
```

### Exemple de Réponse

```json
{
  "results": [
    {
      "mealId": "e9c409fd-b11e-4651-9baf-e8b00cf7da6a",
      "mealName": "Meatball Soup",
      "mealimageurl": "https://file.b18a.io/...",
      "foodType": "Homemade food",
      "cooking_method": "boiling",
      "mealTargetCalories": 300.0,
      "mealTargetProtein": 20.0,
      "mealTargetCarbs": 30.0,
      "mealTargetFats": 10.0,
      "description": "Une soupe de boulettes de viande réconfortante...",
      "mealTypes": ["Soup", "Lunch", "Dinner"],
      "mealIngredients": [...],
      "score": 0.92
    }
  ],
  "total": 1
}
```

>  Le champ `score` indique la similarité sémantique (0-1), où les valeurs plus élevées signifient de meilleures correspondances.

---

##  Documentation de l'API

Une fois le serveur lancé, vous pouvez accéder à la documentation interactive de l'API :

| Documentation | URL |
|---------------|-----|
| **Swagger UI** | http://localhost:8000/docs |


