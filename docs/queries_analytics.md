# Q1 : Recherche textuelle floue sur l'overview
GET movies_clean/_search
{
  "query": {
    "match": {
      "overview": {
        "query": "space battles",
        "fuzziness": "AUTO",
        "analyzer": "movies_analyzer"
      }
    }
  }
}

# Q2 : Filtrage multi-critères avec script de rentabilité
GET movies_clean/_search
{
  "query": {
    "bool": {
      "must": [
        { "range": { "release_date": { "gte": "2010-01-01" } } },
        { "range": { "popularity": { "gte": 30 } } }
      ],
      "filter": [
        { "script": { "script": "doc['revenue'].value > doc['budget'].value" } }
      ]
    }
  }
}

# Q3 : Recherche exacte sur les crédits
GET movies_clean/_search
{
  "query": {
    "term": {
      "credits": "Christopher Nolan"
    }
  }
}

# Q4 : Top films par langue et score
GET movies_clean/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "original_language": "fr" } }
      ],
      "filter": [
        { "range": { "vote_average": { "gte": 7.5 } } }
      ]
    }
  },
  "sort": [{ "popularity": "desc" }]
}

# AGG 1 : Moyenne des notes par genre
GET movies_clean/_search
{
  "size": 0,
  "aggs": {
    "genres_bucket": {
      "terms": { "field": "genres", "size": 10 },
      "aggs": {
        "avg_rating": { "avg": { "field": "vote_average" } }
      }
    }
  }
}

# AGG 2 : Évolution annuelle Revenu vs Budget
GET movies_clean/_search
{
  "size": 0,
  "aggs": {
    "films_par_annee": {
      "date_histogram": {
        "field": "release_date",
        "calendar_interval": "year",
        "format": "yyyy"
      },
      "aggs": {
        "total_revenue": { "sum": { "field": "revenue" } },
        "avg_budget": { "avg": { "field": "budget" } }
      }
    }
  }
}

# CAS INVALIDE : Range sur champ 'text' (overview)
# Erreur attendue : 400 (Fielddata is disabled on text fields by default)
GET movies_clean/_search
{
  "query": {
    "range": {
      "overview": { "gte": 10 }
    }
  }
}