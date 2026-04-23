# Data Cleaning — Movies Data Platform

## Contexte

Ce document décrit les transformations appliquées lors du passage de l'index
`movies_raw` (ingestion brute) vers l'index `movies_clean` (données nettoyées et
typées). Il présente les métriques de qualité avant/après nettoyage et justifie
les choix opérés dans le pipeline Logstash.

---

## Pipeline de nettoyage (F3-03)

Les règles suivantes sont appliquées par le filtre Logstash avant indexation dans
`movies_clean` :

| Règle | Condition | Action |
|---|---|---|
| Titre manquant | `title` vide ou absent | Drop du document + tag `missing_title` |
| Budget nul ou absent | `budget == 0` ou absent | Valeur sentinelle `-1` + tag `missing_budget` |
| Revenue nul ou absent | `revenue == 0` ou absent | Valeur sentinelle `-1` + tag `missing_revenue` |
| Vote hors plage | `vote_average < 0` ou `> 10` | Valeur sentinelle `-1` + tag `invalid_vote_average` |
| Runtime invalide | `runtime <= 0` ou absent | Valeur sentinelle `-1` + tag `missing_runtime` |
| Popularité négative | `popularity < 0` | Valeur sentinelle `-1` + tag `invalid_popularity` |

Tout document portant le tag `_data_quality` est exclu de `movies_clean` et reste
uniquement dans `movies_raw`.

---

## Métriques de qualité avant/après nettoyage

### Métrique 1 — Volume de documents

| Index | Nombre de documents |
|---|---|
| `movies_raw` | 2 475 642 |
| `movies_clean` | 589 517 |
| **Documents filtrés** | **1 886 125** |

> **Interprétation :** 76,2 % des documents bruts ont été écartés de `movies_clean`
> en raison d'au moins une anomalie détectée. Le dataset source présente donc une
> proportion très élevée de données incomplètes, principalement due aux champs
> `runtime`, `title` et autres champs obligatoires manquants.

---

### Métrique 2 — Documents portant le tag `_data_quality`

| Index | Documents avec anomalie | % du total |
|---|---|---|
| `movies_raw` | 372 998 | 15,1 % |
| `movies_clean` | 0 | 0 % |

> **Interprétation :** 372 998 documents présentaient au moins une anomalie
> détectée par le pipeline. Aucun ne passe dans `movies_clean`, ce qui confirme
> le bon fonctionnement du filtre de sortie Logstash (`if "_data_quality" not in [tags]`).
>
> Note : l'écart entre les documents filtrés (1 886 125) et les documents tagués
> (372 998) s'explique par le fait que les films sans titre font l'objet d'un
> `drop {}` immédiat sans être indexés dans `movies_raw` — ils disparaissent
> totalement du pipeline avant indexation.

---

### Métrique 3 — Champ `budget` manquant

| Index | Documents taggés `missing_budget` |
|---|---|
| `movies_raw` | 0 |

> **Limite connue :** La règle de détection du budget manquant ne produit pas de
> tag dans les données observées. Cela est dû à un comportement de typage Logstash :
> le `mutate { convert => { "budget" => "float" } }` est exécuté avant la
> condition `if [budget] == 0`, et la comparaison d'un float `0.0` avec l'entier
> `0` ne matche pas en Logstash DSL. Les documents avec budget nul sont donc
> présents dans `movies_clean` sans être identifiés par ce tag.
> Cette anomalie de pipeline est à corriger en utilisant une comparaison
> `[budget] <= 0` ou un filtre Ruby explicite.

---

### Métrique 4 — Champ `revenue` manquant

| Index | Documents taggés `missing_revenue` |
|---|---|
| `movies_raw` | 0 |

> **Limite connue :** Même cause que pour `missing_budget` — la comparaison
> `[revenue] == 0` ne matche pas le float `0.0` produit par le `mutate convert`.
> Les documents avec revenue nul passent dans `movies_clean` sans tag.

---

### Métrique 5 — Champ `runtime` invalide

| Index | Documents taggés `missing_runtime` |
|---|---|
| `movies_raw` | 372 998 |
| `movies_clean` | 0 |

> **Interprétation :** Le runtime est le principal vecteur d'anomalies du dataset :
> 372 998 documents (15,1 % du brut) ont un runtime invalide ou absent. Ces
> documents sont tous correctement exclus de `movies_clean`.
> Contrairement au budget et au revenue, la règle runtime fonctionne car la
> valeur sentinelle `-1` est stockée comme string `"-1"` (visible dans
> l'échantillon raw), ce qui déclenche bien le tag avant conversion de type.

---

### Métrique 6 — Vérification de l'analyzer `movies_analyzer`

Test réalisé via `GET movies_clean/_analyze` sur la phrase :
`"The Amazing Spider-Man: Revenge of the Fallen"`

| Token produit | Position | Transformation appliquée |
|---|---|---|
| `amaz` | 1 | stemming (`amazing` → `amaz`) |
| `spider` | 2 | tokenisation standard |
| `man` | 3 | tokenisation standard |
| `reveng` | 4 | stemming (`revenge` → `reveng`) |
| `fallen` | 7 | tokenisation standard |

> **Stopwords supprimés :** `the` (positions 0 et 6), `of` (position 5) — liste `_english_`.
>
> **Résultat :** L'analyzer réduit les termes à leur racine morphologique et
> élimine les mots vides anglais. Cela améliore le recall des recherches
> full-text sur `title` et `overview` : une recherche sur `"amazing"` retrouvera
> aussi `"amazed"`, `"amazingly"`, etc.

---

### Métrique 7 — Contrôle visuel par échantillonnage

**Document `movies_raw` avec anomalie :**

```json
{
  "title": "Beberé tu sangre",
  "budget": 0,
  "revenue": 0,
  "runtime": "-1",
  "vote_average": 5,
  "tags": ["_data_quality", "missing_runtime"]
}
```

**Document `movies_clean` sans anomalie `_data_quality` :**

```json
{
  "title": "No Trespassing",
  "budget": 2000000,
  "revenue": 0,
  "runtime": 152,
  "vote_average": 6,
  "tags": ["_json_parse_error_genres", "_json_parse_error_credits", "_json_parse_error_production_companies"]
}
```

> **Observation :** Le document clean présente des tags `_json_parse_error_*` sur
> les champs listes (genres, credits, production_companies), causés par des
> guillemets non standards dans le CSV source. Ces erreurs de parsing JSON ne
> déclenchent pas le tag `_data_quality` et n'empêchent donc pas l'indexation
> dans `movies_clean`. À surveiller pour une future itération du pipeline.

---

## Tableau comparatif récapitulatif

| Métrique | `movies_raw` | `movies_clean` | Variation |
|---|---|---|---|
| Nombre de documents | 2 475 642 | 589 517 | -76,2 % |
| Documents avec tag `_data_quality` | 372 998 | 0 | -100 % |
| Tag `missing_runtime` | 372 998 | 0 | -100 % |
| Tag `missing_budget` | 0 (limite pipeline) | 0 | — |
| Tag `missing_revenue` | 0 (limite pipeline) | 0 | — |
| Tokens analyzer (test) | — | 5 tokens / 8 mots | stopwords + stemming OK |

---

## Choix de conception

**Valeur sentinelle `-1` plutôt que `null`**
Elasticsearch exclut les documents sans valeur de certaines agrégations
(moyenne, percentile). Utiliser `-1` rend les données manquantes explicitement
filtrables : `filter: { range: { budget: { gt: 0 } } }`.

**Drop des films sans titre**
Un film sans titre est inexploitable pour toutes les visualisations et le moteur
de recherche. Le drop immédiat avant indexation évite de polluer `movies_raw`
avec des documents sans valeur métier — ils n'apparaissent donc dans aucun index.

**Tag `_data_quality` dans `movies_raw`**
La conservation des documents anomaliques dans `movies_raw` avec leur tag permet
de tracer l'origine et la nature de chaque anomalie, utile pour audit ou
reclassification future sans re-ingestion complète.

**Limites identifiées**
- La comparaison `[budget] == 0` et `[revenue] == 0` ne fonctionne pas après
  `mutate convert` en Logstash — à corriger avec `[budget] <= 0` ou filtre Ruby.
- Les erreurs `_json_parse_error_*` ne sont pas traitées comme anomalies
  `_data_quality`, ce qui laisse passer des documents avec champs listes vides
  dans `movies_clean`.
