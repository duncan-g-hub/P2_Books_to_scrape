# P2 : Books to scrape - Système de surveillance des prix (Beta)

Projet réalisé dans le cadre de ma formation.  
Il s'agit d'un système de scraping permettant d'extraire toutes les informations et images des livres proposés par le site **Books to Scrape** :  https://books.toscrape.com

L'objectif est de constituer un **système de surveillance des prix**, avec un pipeline simple permettant d'extraire les données, de les transformer et de les stocker.

---

## Fonctionnalités

- Extraction automatique : 
    - Catégories de livres
    - Pages de chaque catégorie
    - URL de chaque livre
    - Informations détaillées : titre, UPC, prix TTC/HT, stock disponible, description, notation, catégorie, URL d'image
- Stockage des données dans un fichier CSV par catégorie 
- Téléchargement des images
- Organisation automatique dans un dossier `/data/<category>/`

---

## Structure du projet

```
P2_Books_to_scrape/
    main.py                         # Script principal
    requirements.txt                # Dépendances
    README.md                       # Documentation

    data/                           # Généré automatiquement (non inclus dans le repo GitHub)
        <category>/                 # Tri des données par catégorie
            <category>.csv          # Stockage des données des livres dans un fichier csv portant le nom de la categorie
            images/                 # Sous dossier images
                <book_title>.jpg    # Chaque image est nommée d’après le titre du livre
```

---

## Technologies utilisées

- Python 3.13
- Requests
- BeautifulSoup4
- CSV
- Pathlib
- re

---

## Installation 

### Prérequis :

- Python 3.10 ou plus récent
- Connexion Internet

### Cloner le repository : 

```bash
git clone https://github.com/duncan-g-hub/P2_Books_to_scrape.git
cd P2_Books_to_scrape/
```

### Installer les dépendances : 

```bash
pip install -r requirements.txt
```

---

## Exécution

```bash
python main.py
```
Les données et images extraites apparaitront automatiquement dans le dossier /data

---

## Résultat attendu

A la fin de l'exécution, vous obtiendrez : 
- un dossier par catégorie 
- un fichier CSV par catégorie contenant les informations des livres
- toutes les images téléchargées 

Ces données pourront ensuite etre utilisées pour : 
- analyser et comparer les prix
- suivre les évolutions tarifaires 
- integrer un pipeline ETL

---

## Contact

Pour toute question :
Duncan GAURAT - duncan.dev@outlook.fr

            
