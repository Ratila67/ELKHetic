# Requêtes Elasticsearch DSL — movies_clean

12 requêtes commentées sur l'index `movies_clean`.  
Dont **7 requêtes `bool`** (exigence : 5 minimum).

---

## Q1 — bool : Films d'action bien notés avec beaucoup de votes

Combine un filtre de genre, un seuil de note et un seuil de votes.  
Utile pour recommander des films d'action populaires et fiables.

```json
GET movies_clean/_search
{
  "query": {
    "bool": {
      "filter": [
        { "term": { "genres": "Action" } },
        { "range": { "vote_average": { "gte": 7.5 } } },
        { "range": { "vote_count": { "gte": 1000 } } }
      ]
    }
  },
  "sort": [{ "vote_average": "desc" }],
  "_source": ["title", "genres", "vote_average", "vote_count"]
}
```

---

## Q2 — bool : Films récents en anglais avec un grand budget

Recherche les grosses productions anglophones sorties depuis 2015.

```json
GET movies_clean/_search
{
  "query": {
    "bool": {
      "must": [
        { "term": { "original_language": "en" } }
      ],
      "filter": [
        { "range": { "release_date": { "gte": "2015-01-01" } } },
        { "range": { "budget": { "gte": 10000000 } } }
      ]
    }
  },
  "sort": [{ "budget": "desc" }],
  "_source": ["title", "release_date", "budget", "original_language"]
}
```

---

## Q3 — bool : Films populaires hors documentaires

Exclut les documentaires pour cibler les films grand public à forte popularité.

```json
GET movies_clean/_search
{
  "query": {
    "bool": {
      "filter": [
        { "range": { "popularity": { "gte": 50 } } }
      ],
      "must_not": [
        { "term": { "genres": "Documentary" } }
      ]
    }
  },
  "sort": [{ "popularity": "desc" }],
  "size": 20,
  "_source": ["title", "genres", "popularity"]
}
```

---

## Q4 — bool : Comédie ou Animation pour la famille avec bonne note

Cible les films familiaux via un `should` sur les genres, avec un minimum de score.

```json
GET movies_clean/_search
{
  "query": {
    "bool": {
      "should": [
        { "term": { "genres": "Comedy" } },
        { "term": { "genres": "Animation" } },
        { "term": { "genres": "Family" } }
      ],
      "minimum_should_match": 1,
      "filter": [
        { "range": { "vote_average": { "gte": 7.0 } } },
        { "range": { "vote_count": { "gte": 500 } } }
      ]
    }
  },
  "_source": ["title", "genres", "vote_average"]
}
```

---

## Q5 — bool : Films rentables (revenue > 5× budget) produits hors USA

Identifie les films étrangers très rentables en comparant budget et revenue,
et en excluant l'anglais comme langue originale.

```json
GET movies_clean/_search
{
  "query": {
    "bool": {
      "must_not": [
        { "term": { "original_language": "en" } }
      ],
      "filter": [
        { "range": { "budget": { "gt": 1000000 } } },
        { "script": {
            "script": {
              "source": "doc['revenue'].value >= doc['budget'].value * 5",
              "lang": "painless"
            }
          }
        }
      ]
    }
  },
  "_source": ["title", "original_language", "budget", "revenue"]
}
```

---

## Q6 — bool + full-text : Recherche thématique "space exploration"

Cherche le thème dans `overview`, `tagline` et `keywords`, en exigeant un statut Released.

```json
GET movies_clean/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "multi_match": {
            "query": "space exploration",
            "fields": ["overview", "tagline", "keywords"],
            "type": "best_fields"
          }
        }
      ],
      "filter": [
        { "term": { "status": "Released" } }
      ]
    }
  },
  "_source": ["title", "overview", "keywords", "vote_average"]
}
```

---

## Q7 — bool : Thriller ou Horror avec durée courte et note correcte

Films de genre tendu avec un runtime ≤ 100 min, accessibles et bien notés.

```json
GET movies_clean/_search
{
  "query": {
    "bool": {
      "should": [
        { "term": { "genres": "Thriller" } },
        { "term": { "genres": "Horror" } }
      ],
      "minimum_should_match": 1,
      "filter": [
        { "range": { "runtime": { "lte": 100 } } },
        { "range": { "vote_average": { "gte": 6.5 } } }
      ]
    }
  },
  "sort": [{ "vote_average": "desc" }],
  "_source": ["title", "genres", "runtime", "vote_average"]
}
```

---

## Q8 — match : Recherche full-text dans les synopsis

Utilise l'analyzer `movies_analyzer` (stemming + stopwords) pour une recherche souple.

```json
GET movies_clean/_search
{
  "query": {
    "match": {
      "overview": {
        "query": "detective murder investigation",
        "operator": "or",
        "minimum_should_match": "2"
      }
    }
  },
  "_source": ["title", "overview", "genres"]
}
```

---

## Q9 — multi_match : Recherche sur titre, synopsis et tagline

Boost sur le titre pour favoriser les correspondances exactes dans le champ principal.

```json
GET movies_clean/_search
{
  "query": {
    "multi_match": {
      "query": "love betrayal revenge",
      "fields": ["title^3", "overview", "tagline^2"],
      "type": "most_fields"
    }
  },
  "_source": ["title", "tagline", "overview"]
}
```

---

## Q10 — range + aggregation : Distribution des films par décennie

Compte les films par tranche de 10 ans pour analyser la production cinématographique dans le temps.

```json
GET movies_clean/_search
{
  "size": 0,
  "aggs": {
    "films_par_decennie": {
      "date_histogram": {
        "field": "release_date",
        "calendar_interval": "year",
        "format": "yyyy",
        "min_doc_count": 1
      }
    }
  }
}
```

---

## Q11 — aggregation : Note moyenne et popularité moyenne par genre

Agrégation imbriquée pour comparer les genres sur deux métriques clés.

```json
GET movies_clean/_search
{
  "size": 0,
  "aggs": {
    "par_genre": {
      "terms": {
        "field": "genres",
        "size": 20
      },
      "aggs": {
        "note_moyenne": {
          "avg": { "field": "vote_average" }
        },
        "popularite_moyenne": {
          "avg": { "field": "popularity" }
        }
      }
    }
  }
}
```

---

## Q12 — aggregation : Top 10 sociétés de production par revenue total

Identifie les studios les plus rentables toutes productions confondues.

```json
GET movies_clean/_search
{
  "size": 0,
  "aggs": {
    "top_studios": {
      "terms": {
        "field": "production_companies",
        "size": 10,
        "order": { "revenue_total": "desc" }
      },
      "aggs": {
        "revenue_total": {
          "sum": { "field": "revenue" }
        },
        "nombre_films": {
          "value_count": { "field": "id" }
        }
      }
    }
  }
}
```
