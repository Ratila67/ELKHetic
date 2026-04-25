# Gestion de Projet — Movies Data Platform

## 1. Méthodologie et Workflow Git

L'équipe a adopté le workflow **Gitflow** pour assurer la stabilité du code et la traçabilité des fonctionnalités.

### Structure des branches
* **`main`** : Version de production stable.
* **`dev`** : Branche d'intégration des fonctionnalités validées.
* **`feature/<id>-<slug>`** : Branches isolées pour chaque ticket (ex: `feature/F6-02-dashboard`).

### Process de validation
* Le push direct sur `main` et `dev` est interdit.
* Chaque ticket fait l'objet d'une **Pull Request (PR)**.
* **Revue de code obligatoire** : Au moins 1 approbation par un pair (Jérome ou Lucien) avant merge.

---

## 2. Répartition des Features

| Membre | Rôle | Principales Responsabilités |
| :--- | :--- | :--- |
| **Jérome** | Lead Technique | Docker Compose, Pipeline Logstash de base, Backend Recherche. |
| **Lucien** | Data Analyst | Custom Analyzer, Visualisations Kibana, Contrôle Qualité. |
| **Koceila** | DevOps / Integrator | Gitflow, Scripts de santé, Normalisation Ruby, Dashboard, Documentation. |

---

## 3. Liste des Pull Requests (Koceila)

| Ticket | Description | Statut | Reviewer |
| :--- | :--- | :--- | :--- |
| F1-02 | Scripts Healthcheck & Docker Ops | Merged | Jérome |
| F2-03 | Initialisation Gitflow | Merged | Lucien |
| F3-02 | Normalisation Ruby des champs listes | Merged | Jérome |
| F4-01 | Mapping explicite `movies_clean` | Merged | Lucien |
| F6-02 | Assemblage Dashboard final | Merged | Lucien |
| F7-02 | Documentation Nettoyage (MD) | Merged | Jérome |

---

## 4. Difficultés Rencontrées et Solutions

### Problèmes de typage Logstash
* **Défi** : Conflit entre les types `float` (convertis via mutate) et les tests de comparaison (`if [field] == 0`) qui échouaient silencieusement.
* **Solution** : Utilisation de valeurs sentinelles (`-1`) et documentation des limites dans le rapport de nettoyage.

### Dépendances de tickets
* **Défi** : Impossibilité de finaliser le dashboard sans les données réelles et le mapping de l'équipe.
* **Solution** : Coordination via Slack/Discord pour synchroniser les merges sur `dev` avant de rafraîchir les Data Views sur Kibana.

### Docker Desktop (Local)
* **Défi** : Erreurs de connexion au moteur Docker (Named Pipes Windows).
* **Solution** : Mise en place d'une procédure de démarrage manuel de Docker Desktop avant l'exécution du `docker compose up`.