# Planning Poker — Movies Data Platform

## Contexte

- **Projet** : Movies Data Platform (stack ELK)
- **Équipe** : Jérome (lead technique), Koceila, Lucien
- **Durée** : 2 semaines
- **Méthode** : Planning Poker, échelle de Fibonacci (1, 2, 3, 5, 8, 13, 21)
- **Unité** : Points de complexité (story points)

---

## Échelle Fibonacci utilisée

| Points | Signification |
|--------|--------------|
| 1 | Trivial — action mécanique, aucune incertitude |
| 2 | Simple — moins d'1h, chemin clair |
| 3 | Modéré — quelques heures, bien borné |
| 5 | Complexe — demi-journée, quelques inconnues |
| 8 | Difficile — journée entière, dépendances multiples |
| 13 | Très complexe — plusieurs jours, forte incertitude |
| 21 | Epic — trop gros, à découper |

---

## Backlog complet — Estimations

### Feature F1 — Infrastructure & Dataset

| ID | Description | Jérome | Koceila | Lucien | **Consensus** | Assigné à |
|----|-------------|--------|---------|--------|---------------|-----------|
| F1-01 | Initialisation du dépôt Git + Gitflow | 2 | 2 | 2 | **2** | Jérome |
| F1-02 | Docker Compose ELK (ES + Kibana + Logstash) | 5 | 5 | 8 | **5** | Jérome |
| F1-03 | Récupération et placement du dataset movies.csv | 2 | 1 | 2 | **2** | Lucien |

### Feature F2 — Ingestion brute (index `movies_raw`)

| ID | Description | Jérome | Koceila | Lucien | **Consensus** | Assigné à |
|----|-------------|--------|---------|--------|---------------|-----------|
| F2-01 | Pipeline Logstash d'ingestion brute | 8 | 5 | 8 | **8** | Jérome |
| F2-02 | Vérification de l'ingestion brute movies_raw | 3 | 2 | 3 | **3** | Lucien |

### Feature F3 — Nettoyage des données

| ID | Description | Jérome | Koceila | Lucien | **Consensus** | Assigné à |
|----|-------------|--------|---------|--------|---------------|-----------|
| F3-01 | Analyse exploratoire du dataset (EDA) | 5 | 5 | 5 | **5** | Koceila |
| F3-02 | Stratégie de nettoyage documentée | 3 | 3 | 3 | **3** | Jérome |
| F3-03 | Gestion des valeurs manquantes et anomalies (Logstash) | 8 | 8 | 8 | **8** | Lucien |
| F3-04 | Indexation movies_clean après nettoyage | 5 | 5 | 5 | **5** | Jérome |

### Feature F4 — Index `movies_clean` et qualité

| ID | Description | Jérome | Koceila | Lucien | **Consensus** | Assigné à |
|----|-------------|--------|---------|--------|---------------|-----------|
| F4-01 | Mapping explicite movies_clean | 5 | 5 | 5 | **5** | Koceila |
| F4-02 | Analyzer personnalisé (title + overview) | 5 | 5 | 5 | **5** | Lucien |
| F4-03 | Contrôle qualité avant/après nettoyage | 5 | 5 | 5 | **5** | Lucien |

### Feature F5 — Requêtes & Recherche

| ID | Description | Jérome | Koceila | Lucien | **Consensus** | Assigné à |
|----|-------------|--------|---------|--------|---------------|-----------|
| F5-01 | Requêtes DSL métier (full-text, agrégations, filtres) | 8 | 5 | 8 | **8** | Jérome |

### Feature F6 — Dashboard Kibana

| ID | Description | Jérome | Koceila | Lucien | **Consensus** | Assigné à |
|----|-------------|--------|---------|--------|---------------|-----------|
| F6-01 | Création des 6-8 visualisations Kibana | 5 | 8 | 8 | **8** | Lucien |
| F6-02 | Assemblage du dashboard Kibana | 5 | 5 | 5 | **5** | Koceila |
| F6-03 | Export .ndjson + docs/kibana_insights.md | 3 | 3 | 3 | **3** | Lucien |

### Feature F7 — Documentation & Démo

| ID | Description | Jérome | Koceila | Lucien | **Consensus** | Assigné à |
|----|-------------|--------|---------|--------|---------------|-----------|
| F7-01 | Dictionnaire de données docs/data_dictionary.md | 3 | 3 | 3 | **3** | Lucien |
| F7-02 | README principal du projet | 2 | 2 | 2 | **2** | Jérome |
| F7-03 | Documentation architecture technique | 3 | 3 | 3 | **3** | Jérome |
| F7-04 | Guide de démarrage (onboarding) | 2 | 2 | 2 | **2** | Koceila |
| F7-05 | Planning Poker docs/planning_poker.md | 1 | 1 | 1 | **1** | Lucien |
| F7-06 | Rapport final / présentation | 5 | 5 | 5 | **5** | Équipe |
| F7-07 | GIF de démo + docs/demo_script.md | 3 | 3 | 3 | **3** | Lucien |

### Feature F8 — Moteur de recherche

| ID | Description | Jérome | Koceila | Lucien | **Consensus** | Assigné à |
|----|-------------|--------|---------|--------|---------------|-----------|
| F8-01 | Conception du moteur de recherche | 5 | 5 | 5 | **5** | Koceila |
| F8-02 | Implémentation du mini moteur de recherche | 8 | 8 | 8 | **8** | Koceila |

---

## Récapitulatif par membre

| Membre | Tickets assignés | Total story points |
|--------|-----------------|-------------------|
| **Jérome** | F1-01, F1-02, F2-01, F3-02, F3-04, F5-01, F7-02, F7-03 | **41** |
| **Koceila** | F3-01, F4-01, F6-02, F7-04, F8-01, F8-02 | **36** |
| **Lucien** | F1-03, F2-02, F3-03, F4-02, F4-03, F6-01, F6-03, F7-01, F7-05, F7-07 | **41** |
| **Équipe** | F7-06 | **5** |
| **Total** | | **123** |

---

## Hypothèses de chiffrage

1. **F1-02 (Docker Compose)** — estimé à 5 malgré la complexité apparente car la stack ELK est bien documentée et les images officielles sont stables. Risque réseau/mémoire pris en compte.
2. **F2-01 (pipeline Logstash)** — estimé à 8 car le CSV ~770k lignes impose des optimisations (batch size, codec) et la gestion des types à l'ingestion est délicate.
3. **F3-03 (nettoyage Logstash)** — estimé à 8 car il cumule la logique conditionnelle (budget=0, vote hors plage, titre vide), le tag `_data_quality`, et la compatibilité avec le pipeline de Jérome.
4. **F6-01 (visualisations Kibana)** — estimé à 8 car 6-8 visualisations variées impliquent des itérations sur les agrégations et le choix des métriques métier pertinentes.
5. **F5-01 (requêtes DSL)** — estimé à 8 car les requêtes full-text avec l'analyzer personnalisé nécessitent de comprendre le pipeline d'analyse pour les calibrer correctement.
6. **F8-02 (moteur de recherche)** — estimé à 8 car c'est une intégration applicative (UI ou script) qui orchestre plusieurs types de requêtes ES.
7. **Tickets documentation (F7-xx)** — volontairement sous-estimés (1-3 pts) sauf F7-06 (5 pts) qui représente la synthèse finale de l'équipe.
8. **Vélocité estimée** : ~60 points / semaine pour l'équipe (3 développeurs, ~2 semaines = 120 pts disponibles). Le backlog de 123 pts est tenu avec une marge minimale — nécessite une bonne parallélisation des sprints.

---

## Répartition par sprint

| Sprint | Objectif | Tickets |
|--------|----------|---------|
| **Sprint 1** | Infrastructure + ingestion brute | F1-01, F1-02, F1-03, F2-01, F2-02 |
| **Sprint 2** | Nettoyage + index movies_clean | F3-01, F3-02, F3-03, F3-04, F4-01, F4-02, F4-03 |
| **Sprint 3** | Requêtes + Dashboard + Moteur | F5-01, F6-01, F6-02, F6-03, F8-01, F8-02 |
| **Sprint 4** | Documentation + Démo + Finalisation | F7-01, F7-02, F7-03, F7-04, F7-05, F7-06, F7-07 |
