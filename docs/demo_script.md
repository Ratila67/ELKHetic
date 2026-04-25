# Scénario de Démonstration — Mini Moteur de Recherche

Ce document détaille les étapes pour démontrer les capacités de recherche full-text et de filtrage de la plateforme.

## 1. Préparation
* **Accès** : Ouvrir un navigateur sur `http://localhost:5000`.
* **Index utilisé** : `movies_clean`.

## 2. Cas de test n°1 : Pertinence et Fuzziness
* **Action** : Taper "Spidre-Man" (avec une faute de frappe) dans la barre de recherche.
* [cite_start]**Résultat attendu** : Grâce à l'option `fuzziness: AUTO`, le moteur doit retourner "The Amazing Spider-Man". 
* [cite_start]**Justification technique** : Le champ `title` a un boost de `^3`, garantissant que les titres exacts remontent en premier.

## 3. Cas de test n°2 : Recherche sémantique (Analyzer)
* **Action** : Rechercher le terme "Amazing".
* **Résultat attendu** : Les films contenant "Amazed" ou "Amazingly" dans l'overview doivent apparaître.
* [cite_start]**Justification technique** : Utilisation du `movies_analyzer`  (stemming) défini au Sprint 2.

## 4. Cas de test n°3 : Filtrage combiné
* **Action** : 
    1. Sélectionner le genre **"Action"**.
    2. Sélectionner la langue **"Anglais"**.
    3. Taper l'année **"2012"**.
* **Résultat attendu** : Liste restreinte de films (ex: Avengers, The Dark Knight Rises).
* [cite_start]**Justification technique** : Utilisation des clauses `filter` et `term`  qui n'impactent pas le score de pertinence mais excluent les documents non correspondants.

## 5. Vérification de la santé
* **Action** : Accéder à `http://localhost:5000/health`.
* [cite_start]**Résultat attendu** : JSON indiquant `"status": "ok"`.