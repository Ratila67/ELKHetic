# Vérification de l'ingestion brute — `movies_raw`

> **Ticket** : F2-02  
> **Auteur** : Lucien  
> **Date** : 2026-04-17  
> **Pipeline** : F2-01 (Jérome) — `logstash.conf` ingestion brute  

---

## 1. Nombre total de documents ingérés

**Requête :**

```
GET movies_raw/_count
```

**Résultat :**

```json
{
  "count": 769631,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  }
}
```

**Analyse :**

- **769 631 documents** indexés dans `movies_raw`.
- 1 shard unique, aucun échec de shard → ingestion complète et cohérente.
- Le count a été vérifié deux fois consécutives pour confirmer la stabilisation (fin d'ingestion).

---

## 2. Échantillon de 5 documents

**Requête :**

```
GET movies_raw/_search?size=5
```

**Résultat** (5 documents retournés) :

| # | `id` | `title` | `original_language` | `release_date` | `vote_average` | `genres` |
|---|------|---------|---------------------|----------------|----------------|----------|
| 1 | 718113 | State of Fear: Murder and Memory on Black Wall Street | en | 2017-04-20 | 0.0 | Documentary-Crime |
| 2 | 720927 | Self-Evident Things | en | 2013-01-01 | 0.0 | null |
| 3 | 717652 | I Am Afraid to Forget Your Face | ar | 2020-09-19 | 6.5 | Drama |
| 4 | 718397 | Dr. Zhang | zh | 2005-01-01 | 0.0 | null |
| 5 | 728783 | Krantodorshi | en | 2020-07-26 | 0.0 | null |

---

## 3. Structure d'un document type

Les **20 champs** définis dans le pipeline Logstash sont tous présents :

| Champ | Exemple (doc #3) | Type ES (brut) | Observation |
|-------|-------------------|----------------|-------------|
| `id` | `"717652"` | text/keyword | Stocké en string (attendu en raw) |
| `title` | `"I Am Afraid to Forget Your Face"` | text/keyword | OK |
| `genres` | `"Drama"` | text/keyword | Valeurs séparées par `-` quand multiples |
| `original_language` | `"ar"` | text/keyword | Code ISO 639-1 |
| `overview` | `"After an 82-day separation..."` | text/keyword | Texte long, certains docs dépassent la limite keyword (voir `_ignored`) |
| `popularity` | `"0.6"` | text/keyword | String, à convertir en float dans `movies_clean` |
| `production_companies` | `"Fig Leaf Studios-Les Cigognes Films"` | text/keyword | Séparées par `-`, beaucoup de nulls |
| `release_date` | `"2020-09-19"` | text/keyword | Format ISO, à typer en date dans `movies_clean` |
| `budget` | `"0.0"` | text/keyword | String, à convertir en float |
| `revenue` | `"0.0"` | text/keyword | String, à convertir en float |
| `runtime` | `"15.0"` | text/keyword | String, à convertir en float |
| `status` | `"Released"` | text/keyword | OK |
| `tagline` | `null` | text/keyword | Souvent null |
| `vote_average` | `"6.5"` | text/keyword | String, à convertir en float |
| `vote_count` | `"4.0"` | text/keyword | String, à convertir en float |
| `credits` | `"Paran Banerjee-Basabdatta..."` | text/keyword | Séparés par `-` |
| `keywords` | `"short film"` | text/keyword | Souvent null |
| `poster_path` | `"/ePdvGMi..."` | text/keyword | Chemin relatif TMDB |
| `backdrop_path` | `null` | text/keyword | Souvent null |
| `recommendations` | `null` | text/keyword | Souvent null |

**Champ ajouté par Logstash :**

| Champ | Exemple | Observation |
|-------|---------|-------------|
| `@timestamp` | `"2026-04-17T08:57:06.400Z"` | Timestamp d'ingestion (pas la date du film) |

---

## 4. Observations et anomalies détectées

### 4.1. Tous les champs sont des strings

C'est le comportement attendu pour une ingestion brute sans mapping explicite. Elasticsearch attribue le type `text` (avec sous-champ `.keyword`) par défaut. La conversion de types (float, date, integer) sera appliquée dans `movies_clean` via le mapping explicite (F4-01) et le pipeline de nettoyage (F3-03).

### 4.2. Valeurs nulles fréquentes

Sur l'échantillon de 5 docs, on observe de nombreux champs à `null` :

- `tagline` : 5/5 null
- `backdrop_path` : 5/5 null
- `recommendations` : 5/5 null
- `credits` : 3/5 null
- `keywords` : 4/5 null
- `production_companies` : 4/5 null
- `genres` : 3/5 null

→ À quantifier à plus grande échelle dans le ticket F4-03 (contrôle qualité).

### 4.3. Valeurs à zéro suspectes

- `budget` : 5/5 à `"0.0"`
- `revenue` : 5/5 à `"0.0"`
- `vote_average` : 4/5 à `"0.0"`
- `vote_count` : 4/5 à `"0.0"`

→ Budget/revenue à 0 ne signifie pas forcément un film gratuit mais souvent une donnée manquante. Sera traité dans F3-03 (gestion des anomalies).

### 4.4. Champ `_ignored`

Certains documents ont `"_ignored": ["overview.keyword"]`. Cela signifie que le texte de l'overview dépasse la limite par défaut d'Elasticsearch pour les champs keyword (256 caractères par défaut via `ignore_above`). Le champ `overview` en tant que `text` reste indexé et cherchable — seul le sous-champ `.keyword` est tronqué. Aucun impact fonctionnel pour notre cas d'usage.

### 4.5. Séparateur multi-valeurs

Les champs `genres`, `production_companies`, `credits` utilisent le caractère `-` comme séparateur. Exemple : `"Documentary-Crime"`, `"Fig Leaf Studios-Les Cigognes Films"`. Ce séparateur devra être pris en compte dans le pipeline de nettoyage si on souhaite éclater ces champs en tableaux.

---

## 5. Verdict

| Critère | Statut |
|---------|--------|
| Index `movies_raw` existe | ✅ |
| Nombre de documents cohérent (769 631) | ✅ |
| 20 champs du CSV présents | ✅ |
| Parsing CSV correct (pas de décalage) | ✅ |
| Header CSV filtré (pas indexé) | ✅ |
| Champs Logstash internes supprimés (`@version`, `host`, `message`, etc.) | ✅ |
| Aucun échec de shard | ✅ |

**Conclusion : l'ingestion brute est conforme et validée.** Les anomalies détectées (nulls, zéros, types string) sont attendues à ce stade et seront traitées dans les tickets de nettoyage (F3-03, F4-01, F4-03).
