# Runbook — Movies ELK Platform

> **Ticket** : F7-03  
> **Auteur** : Jérôme  
> **Stack** : Elasticsearch 8.13 · Kibana 8.13 · Logstash 8.13  
> **Index** : `movies_raw`, `movies_clean`

---

## 1. Prérequis

- Docker Desktop démarré (Engine ≥ 24)
- Docker Compose v2 (`docker compose version`)
- Dataset `movies.csv` présent dans `./DATA/`
- Ports libres : **9200** (ES), **5601** (Kibana)

---

## 2. Démarrer la stack

```bash
./start.sh
```

Le script démarre les trois services et attend que Elasticsearch et Kibana soient `healthy` avant de rendre la main (timeout : ~2,5 min).

**Vérification manuelle :**

```bash
# Elasticsearch
curl http://localhost:9200/_cluster/health?pretty

# Kibana
curl http://localhost:5601/api/status
```

Kibana est accessible sur **http://localhost:5601**.

---

## 3. Arrêter la stack

```bash
./stop.sh
```

Arrête les conteneurs sans supprimer le volume `es_data` — les index sont conservés.

Pour tout supprimer (données incluses) :

```bash
docker compose down -v
```

---

## 4. Vérifier l'ingestion

Logstash ingère `movies.csv` automatiquement au démarrage. L'ingestion complète prend quelques minutes.

```bash
# Nombre de documents dans movies_raw (attendu ≈ 769 631)
curl http://localhost:9200/movies_raw/_count

# Nombre de documents dans movies_clean (données sans anomalie)
curl http://localhost:9200/movies_clean/_count

# Vérifier que le mapping movies_clean est bien appliqué
curl http://localhost:9200/movies_clean/_mapping?pretty
```

---

## 5. Réingérer les données

Si les index sont vides ou corrompus, supprimer et relancer :

```bash
# Supprimer les index
curl -X DELETE http://localhost:9200/movies_raw
curl -X DELETE http://localhost:9200/movies_clean

# Relancer Logstash seul
docker compose restart logstash
```

Logstash repart de zéro (`sincedb_path => "/dev/null"`) et réindexe tout le fichier.

---

## 6. Flux de données

```
movies.csv (DATA/)
    └─► Logstash
          ├─ Parse CSV (20 champs)
          ├─ Normalise listes (genres, keywords, credits, production_companies)
          ├─ Convertit les types (float, integer, date)
          ├─ Gère les anomalies (budget/revenue à 0 → -1, drop si titre manquant)
          ├─► movies_raw     (tous les documents)
          └─► movies_clean   (documents sans tag _data_quality)
```

---

## 7. Logs

```bash
# Logs Logstash en temps réel
docker logs -f logstash

# Logs écrits sur le volume local
ls logs/
```

Les erreurs de parsing JSON des champs liste génèrent le tag `_json_parse_error_<champ>` sur le document.

---

## 8. Problèmes fréquents

### movies_clean est vide

Le tag `_data_quality` filtre les documents vers `movies_clean`. Vérifier qu'aucune condition de la pipeline ne taggue tous les documents :

```bash
curl http://localhost:9200/movies_clean/_count
curl http://localhost:9200/movies_raw/_search?q=tags:_data_quality&size=1
```

### Kibana affiche "No results"

Vérifier que le Data View est configuré sur `movies_clean` (ou `movies_raw`) dans Kibana → **Stack Management → Data Views**.

### Port 9200 ou 5601 déjà utilisé

```bash
# Identifier le processus
netstat -ano | findstr :9200

# Modifier le port dans docker-compose.yml si nécessaire
```

### Elasticsearch passe en statut `red`

```bash
curl http://localhost:9200/_cluster/health?pretty
curl http://localhost:9200/_cat/indices?v
```

Un index en état `red` indique des shards non assignés. Avec un nœud unique c'est rare — généralement lié à un manque de mémoire heap. Vérifier `ES_JAVA_OPTS` dans `docker-compose.yml` (actuellement `-Xms1g -Xmx1g`).

---

## 9. Commandes utiles

```bash
# État des conteneurs
docker compose ps

# Santé du cluster
curl http://localhost:9200/_cluster/health?pretty

# Liste des index
curl http://localhost:9200/_cat/indices?v

# Exemple de document movies_clean
curl http://localhost:9200/movies_clean/_search?size=1&pretty

# Appliquer manuellement le mapping (si index supprimé)
curl -X PUT http://localhost:9200/movies_clean \
     -H "Content-Type: application/json" \
     -d @elasticsearch/mappings/movies_clean_mapping.json
```
