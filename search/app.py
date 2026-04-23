from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
INDEX = "movies_clean"

HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Movies Search</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: sans-serif; background: #0f0f0f; color: #eee; padding: 2rem; }
    h1 { margin-bottom: 1.5rem; font-size: 1.6rem; color: #fff; }
    .search-bar { display: flex; gap: .5rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
    input, select { background: #1e1e1e; border: 1px solid #333; color: #eee;
                    padding: .5rem .75rem; border-radius: 6px; font-size: .95rem; }
    input[type=text] { flex: 1; min-width: 200px; }
    button { background: #e50914; color: #fff; border: none; padding: .5rem 1.2rem;
             border-radius: 6px; cursor: pointer; font-size: .95rem; }
    button:hover { background: #f40612; }
    #total { font-size: .85rem; color: #888; margin-bottom: 1rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; }
    .card { background: #1c1c1c; border-radius: 8px; padding: 1rem; border: 1px solid #2a2a2a; }
    .card h3 { font-size: 1rem; margin-bottom: .4rem; color: #fff; }
    .meta { font-size: .8rem; color: #888; margin-bottom: .4rem; }
    .score { display: inline-block; background: #e50914; color: #fff; font-size: .75rem;
             padding: .15rem .45rem; border-radius: 4px; margin-left: .4rem; }
    .genres { font-size: .78rem; color: #aaa; }
    .overview { font-size: .8rem; color: #999; margin-top: .5rem;
                display: -webkit-box; -webkit-line-clamp: 3;
                -webkit-box-orient: vertical; overflow: hidden; }
  </style>
</head>
<body>
  <h1>🎬 Movies Search</h1>
  <div class="search-bar">
    <input type="text" id="q" placeholder="Titre, synopsis, mot-clé…" />
    <select id="genre">
      <option value="">Tous les genres</option>
      <option>Action</option><option>Adventure</option><option>Animation</option>
      <option>Comedy</option><option>Crime</option><option>Documentary</option>
      <option>Drama</option><option>Family</option><option>Fantasy</option>
      <option>Horror</option><option>Music</option><option>Mystery</option>
      <option>Romance</option><option>Science Fiction</option><option>Thriller</option>
      <option>War</option><option>Western</option>
    </select>
    <select id="language">
      <option value="">Toutes les langues</option>
      <option value="en">Anglais</option>
      <option value="fr">Français</option>
      <option value="es">Espagnol</option>
      <option value="ja">Japonais</option>
      <option value="ko">Coréen</option>
    </select>
    <input type="number" id="year" placeholder="Année" min="1900" max="2030" style="width:90px" />
    <button onclick="search()">Rechercher</button>
  </div>
  <div id="total"></div>
  <div class="grid" id="results"></div>

  <script>
    document.getElementById("q").addEventListener("keydown", e => {
      if (e.key === "Enter") search();
    });

    async function search() {
      const params = new URLSearchParams();
      const q = document.getElementById("q").value.trim();
      const genre = document.getElementById("genre").value;
      const language = document.getElementById("language").value;
      const year = document.getElementById("year").value;
      if (q) params.set("q", q);
      if (genre) params.set("genre", genre);
      if (language) params.set("language", language);
      if (year) params.set("year", year);

      const res = await fetch("/search?" + params.toString());
      const data = await res.json();

      document.getElementById("total").textContent =
        data.total > 0 ? data.total + " résultats" : "Aucun résultat";

      document.getElementById("results").innerHTML = data.results.map(m => `
        <div class="card">
          <h3>${m.title} <span class="score">★ ${m.vote_average ?? "–"}</span></h3>
          <div class="meta">${m.year ?? "–"} · ${m.original_language ?? ""}</div>
          <div class="genres">${Array.isArray(m.genres) ? m.genres.join(", ") : (m.genres ?? "")}</div>
          <div class="overview">${m.overview ?? ""}</div>
        </div>
      `).join("");
    }

    search();
  </script>
</body>
</html>
"""


def build_query(q, genre, language, year):
    must = []
    filters = []

    if q:
        must.append({
            "multi_match": {
                "query": q,
                "fields": ["title^3", "overview", "tagline^2", "keywords"],
                "type": "best_fields",
                "analyzer": "movies_analyzer",
                "fuzziness": "AUTO"
            }
        })

    if genre:
        filters.append({"term": {"genres": genre}})
    if language:
        filters.append({"term": {"original_language": language}})
    if year:
        filters.append({
            "range": {
                "release_date": {
                    "gte": f"{year}-01-01",
                    "lte": f"{year}-12-31"
                }
            }
        })

    if not must and not filters:
        return {"match_all": {}}

    return {
        "bool": {
            **({"must": must} if must else {}),
            **({"filter": filters} if filters else {})
        }
    }


@app.get("/")
def index():
    return render_template_string(HTML)


@app.get("/search")
def search():
    q = request.args.get("q", "").strip()
    genre = request.args.get("genre", "").strip()
    language = request.args.get("language", "").strip()
    year = request.args.get("year", "").strip()
    size = min(int(request.args.get("size", 20)), 100)

    payload = {
        "query": build_query(q, genre, language, year),
        "size": size,
        "_source": ["title", "genres", "original_language", "release_date",
                    "vote_average", "overview", "popularity"],
        "sort": [
            {"_score": "desc"},
            {"popularity": "desc"}
        ]
    }

    try:
        resp = requests.post(
            f"{ES_HOST}/{INDEX}/_search",
            json=payload,
            timeout=5
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return jsonify({"error": str(e)}), 502

    hits = data.get("hits", {})
    total = hits.get("total", {}).get("value", 0)

    results = []
    for hit in hits.get("hits", []):
        src = hit["_source"]
        year_val = None
        if src.get("release_date"):
            year_val = str(src["release_date"])[:4]
        results.append({
            "title": src.get("title"),
            "year": year_val,
            "genres": src.get("genres"),
            "original_language": src.get("original_language"),
            "vote_average": src.get("vote_average"),
            "overview": src.get("overview"),
        })

    return jsonify({"total": total, "results": results})


@app.get("/health")
def health():
    try:
        resp = requests.get(f"{ES_HOST}/_cluster/health", timeout=3)
        return jsonify({"status": "ok", "elasticsearch": resp.json().get("status")})
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
