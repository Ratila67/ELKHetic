## Dataset

Ce projet utilise le dataset **"Millions of Movies"** d'Akshay Pawar (Kaggle).

- **Source** : https://www.kaggle.com/datasets/akshaypawar7/millions-of-movies/versions/67
- **Fichier attendu** : `movies.csv` (~500 Mo, ~700k films)
- **Emplacement** : `./DATA/movies.csv`

> Le fichier `movies.csv` n'est **pas versionné** (trop volumineux). Chaque
> membre de l'équipe doit le télécharger manuellement.

### Téléchargement manuel

1. Créer un compte Kaggle si nécessaire : https://www.kaggle.com/account/login
2. Ouvrir la page du dataset : https://www.kaggle.com/datasets/akshaypawar7/millions-of-movies/versions/67
3. Cliquer sur **Download** → récupérer le zip
4. Dézipper et placer `movies.csv` dans `./DATA/` à la racine du repo

```bash
# Depuis la racine du repo
mkdir -p DATA
cd DATA
kaggle datasets download -d akshaypawar7/millions-of-movies
unzip millions-of-movies.zip
rm millions-of-movies.zip
cd ..
```

### Vérification

```bash
ls -lh DATA/movies.csv     # doit exister, ~500 Mo
head -1 DATA/movies.csv    # doit afficher les en-têtes CSV
wc -l DATA/movies.csv      # doit afficher ~700k lignes
```