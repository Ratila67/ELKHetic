# Demo Script — Movies Data Platform

## Durée
~47 secondes

## Séquence 1 — Vérification de la stack
- Commande `docker compose ps` : 3 containers UP (elasticsearch, kibana, logstash)
- Navigation vers `http://localhost:9200` : réponse JSON Elasticsearch

## Séquence 2 — Dashboard Kibana
- Navigation vers `http://localhost:5601`
- Ouverture du dashboard Movies Data Platform
- Défilement des visualisations

## Séquence 3 — Moteur de recherche
- Navigation vers `http://localhost:5000`
- Filtre par genre : `Action`
- Filtre par pays : `Japon`
- Filtre par année : `1994`