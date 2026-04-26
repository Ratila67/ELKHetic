# Kibana Insights — Movies Data Platform

> Dashboard : **Movies Insights**  
> Index source : `movies_clean`  
> Export : `kibana/dashboard_export.ndjson`  
> Visualisations : 8 (V1 à V8)

---

## Visualisations du dashboard

| ID  | Titre                              | Type           | Champ(s) analysé(s)                   | Question métier                                              |
|-----|------------------------------------|----------------|----------------------------------------|--------------------------------------------------------------|
| V1  | Top genres                         | Bar empilée    | `genres`                              | Quels sont les genres les plus représentés dans le catalogue ? |
| V2  | Distribution des notes             | Histogramme    | `vote_average`                        | Comment se distribuent les notes des films ?                 |
| V3  | Évolution de la production par année | Courbe        | `release_date`                        | Comment a évolué le volume de production cinématographique ? |
| V4  | Top 10 langues originales          | Bar horizontal | `original_language`                   | Quelles langues dominent la production mondiale ?            |
| V5  | Budget vs Revenue                  | Heatmap        | `budget`, `revenue`                   | Existe-t-il une corrélation entre budget et recettes ?       |
| V6  | Statuts des films                  | Donut          | `status`                              | Quelle proportion des films est réellement sortie en salle ? |
| V7  | Top sociétés de production         | Bar horizontal | `production_companies`                | Quels studios dominent le catalogue en volume ?              |
| V8  | Popularité moyenne par genre       | Bar verticale  | `genres`, `popularity`                | Quels genres génèrent le plus d'engagement ?                 |

---

## Insights métier

### Insight 1 — La domination écrasante de quelques genres (V1)

La visualisation **V1 – Top genres** (bar chart empilé, top 10 valeurs du champ `genres`) révèle une concentration marquée de la production cinématographique autour de trois grandes familles : **Drama**, **Comedy** et **Thriller**. Ces genres représentent structurellement la majorité des films indexés dans `movies_clean`.

**Implication métier :** un système de recommandation basé sur ce catalogue sera naturellement biaisé vers ces genres. Pour garantir la diversité des résultats de recherche, il est conseillé d'introduire un facteur de pondération inverse à la fréquence du genre (`genre_boost_factor`), afin de ne pas systématiquement enfouir les genres de niche (Animation, Documentary, etc.) dans les résultats.

---

### Insight 2 — Une distribution des notes centrée sur la médiocrité (V2)

L'histogramme **V2 – Distribution des notes** (filtre `vote_average > 0`, intervalle automatique) montre une distribution unimodale avec un pic concentré entre **5.5 et 7.0**. Les films très mal notés (< 3) et excellemment notés (> 8) sont minoritaires.

**Implication métier :** la note moyenne n'est pas un discriminant suffisant pour classer les films entre eux, car la grande majorité se situe dans la même plage. Pour le moteur de recherche, il sera pertinent de combiner `vote_average` avec `vote_count` (popularité du vote) pour éviter de surclasser des films avec peu de votes mais une note artificielle haute. Un score composite de type `score = vote_average * log(vote_count + 1)` serait plus robuste.

---

### Insight 3 — L'explosion de la production après les années 2000 (V3)

La courbe **V3 – Évolution de la production par année** (date histogram sur `release_date`, granularité annuelle) met en évidence une **croissance exponentielle** du nombre de films produits à partir du début des années 2000, avec une accélération très marquée entre 2010 et aujourd'hui.

**Implication métier :** les films récents sur-représentent mécaniquement le dataset. Sans correctif temporel, les analyses de tendances (genres populaires, langues dominantes) refléteront avant tout la production contemporaine. Pour des analyses historiques fiables, il est indispensable d'utiliser le **filtre temporel du dashboard** (time picker Kibana) pour segmenter les analyses par décennie.

---

### Insight 4 — La domination de l'anglais, mais une production multilingue significative (V4)

Le bar chart horizontal **V4 – Top 10 langues originales** (champ `original_language`, top 10 par count) confirme que l'anglais (`en`) représente de très loin la première langue de production. Cependant, le français (`fr`), l'espagnol (`es`), l'hindi (`hi`) et l'italien (`it`) apparaissent en bonne position, soulignant la **dimension internationale** réelle du catalogue.

**Implication métier :** le moteur de recherche doit gérer le multilinguisme. L'analyzer personnalisé défini en **F4-02** (tokenizer standard + lowercase + stemmer + stopwords) est configuré pour l'anglais par défaut. Il serait pertinent d'envisager un analyzer par langue (`analyzer_fr`, `analyzer_es`) sur les champs `title` et `overview` pour les langues les plus représentées, afin d'améliorer la pertinence des recherches en langues non-anglaises.

---

### Insight 5 — Rentabilité : une corrélation budget/recettes non linéaire (V5)

La heatmap **V5 – Budget vs Revenue** (filtre `budget > 0 AND revenue > 0`, axes en histogramme) visualise la densité des films selon leur budget et leurs recettes. La concentration des points se situe dans les **tranches basses des deux axes**, avec quelques films isolés dans les zones de budget et recettes très élevés.

**Implication métier :** la majorité des films avec des données financières renseignées sont des productions à petit budget avec des recettes modestes. Les blockbusters (budget > 100M$) sont statistiquement rares mais représentent probablement une part disproportionnée des recettes totales. Ce constat justifie le traitement des valeurs à 0 effectué en **F3-03** (tag `_data_quality`) : les films sans données financières constituent une catégorie distincte, pas des outliers à supprimer.

---

## Structure des fichiers livrés

```
kibana/
└── dashboard_export.ndjson     ← export complet (10 objets : 1 index-pattern + 8 lens + 1 dashboard)

docs/
└── kibana_insights.md          ← ce fichier
```

---

## Comment réimporter le dashboard

```bash
# Depuis Kibana UI
# Stack Management → Saved Objects → Import → sélectionner dashboard_export.ndjson
# Cocher "Overwrite" si des objets existent déjà

# Ou via API
curl -X POST "http://localhost:5601/api/saved_objects/_import?overwrite=true" \
  -H "kbn-xsrf: true" \
  --form file=@kibana/dashboard_export.ndjson
```
