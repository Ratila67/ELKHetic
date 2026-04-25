# Dictionnaire de données — Index `movies_clean`

**Projet** : Movies Data Platform  
**Index Elasticsearch** : `movies_clean`  
**Analyzer personnalisé** : `movies_analyzer` (tokenizer `standard` → `lowercase` → `movies_stop` → `movies_stemmer`)  
**Dernière mise à jour** : Sprint 2  
**Auteurs** : Lucien, Koceila (mapping F4-01), Lucien (analyzer F4-02)

---

## Analyzer `movies_analyzer`

| Composant | Type | Paramètre |
|---|---|---|
| Tokenizer | `standard` | — |
| Filtre 1 | `lowercase` | — |
| Filtre 2 | `stop` (`movies_stop`) | `stopwords: _english_` |
| Filtre 3 | `stemmer` (`movies_stemmer`) | `language: english` |

Appliqué aux champs : `title`, `overview`, `tagline`, `recommendations`

---

## Champs de l'index

### `id`

| Attribut | Valeur |
|---|---|
| **Type ES** | `integer` |
| **Indexé** | Oui |
| **Description** | Identifiant unique du film, issu du dataset source Kaggle. Sert de clé primaire pour les jointures et la déduplication. |
| **Exemple** | `550` |
| **Justification du type** | `integer` : valeur numérique entière sans décimale, utilisée pour les filtres exacts et le tri — `keyword` serait superflu. |

---

### `title`

| Attribut | Valeur |
|---|---|
| **Type ES** | `text` + sous-champ `keyword` |
| **Analyzer** | `movies_analyzer` (champ principal) / aucun (`.keyword`) |
| **`ignore_above`** | 256 (sous-champ `.keyword`) |
| **Indexé** | Oui |
| **Description** | Titre du film en langue d'exploitation principale. Le champ `text` permet la recherche full-text avec stemming et suppression des stopwords. Le sous-champ `.keyword` permet le tri exact, les agrégations et les filtres stricts. |
| **Exemple** | `"Fight Club"` |
| **Justification du type** | Double mapping `text`/`keyword` : `text` pour la recherche (requêtes `match`, `multi_match`), `keyword` pour les agrégations Kibana (ex. top films par popularité). |

---

### `genres`

| Attribut | Valeur |
|---|---|
| **Type ES** | `keyword` |
| **Indexé** | Oui |
| **Description** | Genre(s) du film. Champ multi-valué : un film peut appartenir à plusieurs genres (ex. Action, Thriller). Utilisé pour les agrégations par genre et les filtres de facettes. |
| **Exemple** | `["Action", "Drama"]` |
| **Justification du type** | `keyword` : les genres sont des valeurs contrôlées, recherchées en correspondance exacte et agrégées. Un analyzer de stemming dénaturerait les termes ("Drama" → "drama" acceptable, mais "Animation" → "anim" serait problématique). |

---

### `original_language`

| Attribut | Valeur |
|---|---|
| **Type ES** | `keyword` |
| **Indexé** | Oui |
| **Description** | Code de langue ISO 639-1 de la langue originale du film (2 caractères). |
| **Exemple** | `"en"`, `"fr"`, `"ja"` |
| **Justification du type** | `keyword` : code court, valeur contrôlée, uniquement utilisé pour des filtres exacts et des agrégations (répartition par langue). |

---

### `overview`

| Attribut | Valeur |
|---|---|
| **Type ES** | `text` |
| **Analyzer** | `movies_analyzer` |
| **Indexé** | Oui |
| **Description** | Synopsis du film en texte libre. Champ central du moteur de recherche full-text — les requêtes utilisateur portent prioritairement sur ce champ. |
| **Exemple** | `"A ticking-time-bomb insomniac and a slippery soap salesman channel primal male aggression into a shocking new form of therapy."` |
| **Justification du type** | `text` avec `movies_analyzer` : le synopsis bénéficie du stemming (recherche de "fight" retrouve "fighting") et de la suppression des stopwords pour des scores de pertinence plus précis. Pas de sous-champ `keyword` car les agrégations sur synopsis n'ont pas de sens métier. |

---

### `popularity`

| Attribut | Valeur |
|---|---|
| **Type ES** | `float` |
| **Indexé** | Oui |
| **Description** | Score de popularité calculé par TMDB. Valeur composite prenant en compte les vues, les votes et les interactions récentes. Utilisé pour le tri par défaut et les visualisations de tendances. |
| **Exemple** | `63.512` |
| **Justification du type** | `float` : valeur décimale continue, utilisée dans des tris, des ranges et des agrégations numériques (avg, max). |

---

### `production_companies`

| Attribut | Valeur |
|---|---|
| **Type ES** | `keyword` |
| **Indexé** | Oui |
| **Description** | Nom(s) de la ou des société(s) de production du film. Champ multi-valué. |
| **Exemple** | `["Warner Bros.", "Legendary Entertainment"]` |
| **Justification du type** | `keyword` : les noms de sociétés sont recherchés en correspondance exacte et agrégés (ex. top studios par nombre de films). Le stemming serait contre-productif sur des noms propres. |

---

### `release_date`

| Attribut | Valeur |
|---|---|
| **Type ES** | `date` |
| **Format** | ISO 8601 (`yyyy-MM-dd`) |
| **Indexé** | Oui |
| **Description** | Date de sortie officielle du film. Utilisée pour les filtres temporels, les histogrammes par année/décennie et les analyses de tendances. |
| **Exemple** | `"1999-10-15"` |
| **Justification du type** | `date` : permet les requêtes `range`, les agrégations `date_histogram` et le tri chronologique natif dans Kibana. |

---

### `budget`

| Attribut | Valeur |
|---|---|
| **Type ES** | `float` |
| **Indexé** | Oui |
| **Description** | Budget de production du film en dollars USD. Les valeurs à `0` indiquent une donnée manquante ou non renseignée (traitées par F3-03 avec le tag `_data_quality`). |
| **Exemple** | `63000000.0` |
| **Justification du type** | `float` : valeur monétaire potentiellement grande, utilisée dans des agrégations (avg budget par genre, corrélation budget/revenue). |

---

### `revenue`

| Attribut | Valeur |
|---|---|
| **Type ES** | `float` |
| **Indexé** | Oui |
| **Description** | Recettes au box-office mondial en dollars USD. Les valeurs à `0` indiquent une donnée manquante (traitées par F3-03). |
| **Exemple** | `100853753.0` |
| **Justification du type** | `float` : même justification que `budget` — agrégations numériques, calcul de ROI (`revenue / budget`). |

---

### `runtime`

| Attribut | Valeur |
|---|---|
| **Type ES** | `float` |
| **Indexé** | Oui |
| **Description** | Durée du film en minutes. |
| **Exemple** | `139.0` |
| **Justification du type** | `float` : durée décimale possible (ex. 94.5 min), utilisée pour des agrégations et des filtres de range (films > 2h). |

---

### `status`

| Attribut | Valeur |
|---|---|
| **Type ES** | `keyword` |
| **Indexé** | Oui |
| **Description** | Statut de sortie du film. Valeurs possibles issues de TMDB : `Released`, `Post Production`, `In Production`, `Planned`, `Canceled`, `Rumored`. |
| **Exemple** | `"Released"` |
| **Justification du type** | `keyword` : valeur contrôlée issue d'un enum, utilisée pour des filtres exacts et des agrégations (répartition par statut). |

---

### `tagline`

| Attribut | Valeur |
|---|---|
| **Type ES** | `text` |
| **Analyzer** | `movies_analyzer` |
| **Indexé** | Oui |
| **Description** | Accroche marketing du film. Texte court et idiomatique, inclus dans le moteur de recherche full-text pour enrichir la pertinence. |
| **Exemple** | `"Mischief. Mayhem. Soap."` |
| **Justification du type** | `text` avec `movies_analyzer` : la tagline bénéficie du full-text pour les recherches thématiques. Pas de `keyword` car aucune agrégation métier sur ce champ. |

---

### `vote_average`

| Attribut | Valeur |
|---|---|
| **Type ES** | `float` |
| **Indexé** | Oui |
| **Description** | Note moyenne des utilisateurs TMDB sur une échelle de 0 à 10. Les valeurs hors plage `[0, 10]` sont filtrées par F3-03 (tag `_data_quality`). |
| **Exemple** | `8.4` |
| **Justification du type** | `float` : valeur décimale sur échelle continue, utilisée pour les tris, ranges et agrégations (avg note par genre, distribution des notes). |

---

### `vote_count`

| Attribut | Valeur |
|---|---|
| **Type ES** | `integer` |
| **Indexé** | Oui |
| **Description** | Nombre de votes TMDB ayant contribué à `vote_average`. Utilisé pour pondérer la fiabilité de la note (un film avec 5 votes à 9.0 est moins fiable qu'un film avec 10 000 votes à 8.0). |
| **Exemple** | `24156` |
| **Justification du type** | `integer` : compteur entier, utilisé dans des agrégations et comme pondération dans les requêtes `function_score`. |

---

### `credits`

| Attribut | Valeur |
|---|---|
| **Type ES** | `keyword` |
| **Indexé** | Oui |
| **Description** | Noms des acteurs et membres de l'équipe technique principaux. Champ multi-valué. Permet les recherches et agrégations par nom de personne (ex. filmographie d'un acteur). |
| **Exemple** | `["Brad Pitt", "Edward Norton", "David Fincher"]` |
| **Justification du type** | `keyword` : les noms propres sont recherchés en correspondance exacte. Le stemming altèrerait les patronymes. |

---

### `keywords`

| Attribut | Valeur |
|---|---|
| **Type ES** | `keyword` |
| **Indexé** | Oui |
| **Description** | Mots-clés thématiques associés au film par la communauté TMDB. Champ multi-valué. Enrichit les possibilités de filtrage et de recommandation. |
| **Exemple** | `["based on novel", "fight club", "underground"]` |
| **Justification du type** | `keyword` : les tags thématiques sont utilisés en correspondance exacte pour les filtres et les agrégations (nuage de tags, films par thématique). |

---

### `poster_path`

| Attribut | Valeur |
|---|---|
| **Type ES** | `keyword` |
| **Indexé** | **Non** (`"index": false`) |
| **Description** | Chemin relatif vers l'affiche du film sur le CDN TMDB. Champ purement applicatif, non destiné à la recherche ni aux agrégations. |
| **Exemple** | `"/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg"` |
| **Justification du type** | `keyword` non indexé : stockage de l'URL pour affichage dans le dashboard/moteur de recherche. L'indexation serait un gaspillage de ressources — ce champ n'est jamais utilisé dans une requête. |

---

### `backdrop_path`

| Attribut | Valeur |
|---|---|
| **Type ES** | `keyword` |
| **Indexé** | **Non** (`"index": false`) |
| **Description** | Chemin relatif vers l'image de fond (backdrop) du film sur le CDN TMDB. Même usage que `poster_path`, destiné à l'affichage. |
| **Exemple** | `"/fCayJrkfRaCRCTh8GqN30f8oyQF.jpg"` |
| **Justification du type** | `keyword` non indexé : identique à `poster_path` — champ de rendu visuel, aucune valeur analytique. |

---

### `recommendations`

| Attribut | Valeur |
|---|---|
| **Type ES** | `text` |
| **Analyzer** | `movies_analyzer` |
| **Indexé** | Oui |
| **Description** | Titres ou descriptions de films recommandés en association avec ce film, issus de l'API TMDB. Utilisé pour enrichir le contexte full-text du document dans le moteur de recherche. |
| **Exemple** | `"The Game Se7en The Usual Suspects"` |
| **Justification du type** | `text` avec `movies_analyzer` : ce champ est un texte libre de titres concaténés, bénéficiant du stemming pour la recherche associative. Pas d'agrégation attendue sur ce champ. |

---

## Récapitulatif des types

| Type ES | Champs |
|---|---|
| `integer` | `id`, `vote_count` |
| `float` | `popularity`, `budget`, `revenue`, `runtime`, `vote_average` |
| `date` | `release_date` |
| `text` (avec `movies_analyzer`) | `title`, `overview`, `tagline`, `recommendations` |
| `text` + `keyword` (multi-field) | `title` (`.keyword` pour agrégations) |
| `keyword` (indexé) | `genres`, `original_language`, `production_companies`, `status`, `credits`, `keywords` |
| `keyword` (non indexé) | `poster_path`, `backdrop_path` |

---

## Notes de qualité des données

Les champs suivants peuvent contenir des valeurs manquantes ou anomalies, traitées par le pipeline **F3-03** :

| Champ | Anomalie connue | Traitement F3-03 |
|---|---|---|
| `budget` | Valeur `0` = donnée manquante | Tag `_data_quality` |
| `revenue` | Valeur `0` = donnée manquante | Tag `_data_quality` |
| `vote_average` | Valeurs hors `[0, 10]` | Filtrage / tag `_data_quality` |
| `title` | Champ vide ou null | Document rejeté ou tagué |
