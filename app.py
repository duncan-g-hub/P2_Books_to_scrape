import re
from pathlib import Path
import csv
from bs4 import BeautifulSoup
import requests

CUR_DIR = Path(__file__).resolve().parent
DATA_DIR = CUR_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

main_url = "https://books.toscrape.com"


# _____obtenir le code html d'une page via une requete sur un url_____
def _get_soup_from_request(url):
    r = requests.get(url)
    if not r.status_code == 200:
        raise ValueError("Impossible de récupérer l'url.")
    return BeautifulSoup(r.content, "html.parser")


# _____Récupérer les urls de chaque catégories_____
def get_categories_urls(main_url) -> list:
    soup = _get_soup_from_request(main_url)
    nav_list = soup.find("ul", class_="nav nav-list")
    categories = nav_list.find_all("li")[1:]
    categories_urls = []
    for category in categories:
        category_url = f"{main_url}/{category.find("a").get("href")}"
        categories_urls.append(category_url)
    return categories_urls


# _____ créer une liste d'url en fonction du nombre de pages d'une catégorie_____
def get_pages_urls_from_category(category_url) -> list:
    soup = _get_soup_from_request(category_url)
    pages_urls = [category_url]

    # ___conditionner le changement de page en fonction du nombre de page___
    next_btn = soup.find("li", class_="next")
    while next_btn:
        next_url = next_btn.find("a").get("href")
        cat_url = category_url.split("/")
        cat_url[-1] = next_url
        next_url = "/".join(cat_url)
        pages_urls.append(next_url)
        soup = _get_soup_from_request(next_url)
        next_btn = soup.find("li", class_="next")

    return pages_urls


# _____récupérer toutes les url d'une catégorie_____
def get_products_urls_from_category(pages_urls) -> list:
    products_urls = []
    for page_url in pages_urls:
        soup = _get_soup_from_request(page_url)

        # ___récupérer la totalité des urls de la page dans une liste___
        products = soup.find("ol", class_="row")
        products = products.find_all("li")
        for product in products:
            product_url = product.find("a").get("href").replace("../../..", f"{main_url}/catalogue")
            products_urls.append(product_url)
    return products_urls


# _____extraction des informations des livres_____
def get_products_informations(product_urls: list) -> list[dict]:
    products_informations = []

    for product_url in product_urls:
        soup = _get_soup_from_request(product_url)

        # ___url___
        product_page_url = product_url

        # ___title___
        title = soup.find("h1").get_text(strip=True)

        # ___category___
        breadcrumb = soup.find("ul", class_="breadcrumb")
        category = breadcrumb.find_all("li")[-2].get_text(strip=True)

        # ___review_rating___
        rate = soup.find("p", class_="star-rating")
        review_rating = rate["class"][-1]

        # ___image_url___
        image = soup.find("img")
        image_url = image["src"].replace("../..", main_url)

        # ___description___
        description_header = soup.find("div", id="product_description")
        if description_header:
            product_description = description_header.find_next("p").get_text(strip=True)
        else:
            product_description = ""

        # ___product informations___
        informations = soup.find(class_="table table-striped")
        informations = informations.find_all("td")
        upc = informations[0].string
        price_excluding_tax = informations[2].string
        price_including_tax = informations[3].string
        number_available = informations[5].string

        # ___création du dict des informations___
        product_informations = {"title": title,
                                "url": product_page_url,
                                "category": category,
                                "review_rating": review_rating,
                                "image_url": image_url,
                                "description": product_description,
                                "upc": upc,
                                "price_excluding_tax": price_excluding_tax,
                                "price_including_tax": price_including_tax,
                                "number_available": number_available
                                }

        products_informations.append(product_informations)
    return products_informations


def transform_products_informations(products_informations) -> list[dict]:
    products_informations_transformed = []
    for product_informations in products_informations:

        # ___title_name___
        title = product_informations.get('title')
        # re.sub pour remplacer les caracteres non pris en compte par windows (save images)
        product_informations['title'] = re.sub(r'[/\\:?*"<>]', '',title)

        # ___nombre en stock en int___
        number_available = product_informations["number_available"]
        product_informations["number_available"] = int(number_available.split()[2].strip("("))

        # ___review_rating en note x/5___
        review_rating = product_informations["review_rating"]
        if review_rating == "One":
            product_informations["review_rating"] = "1/5"
        elif review_rating == "Two":
            product_informations["review_rating"] = "2/5"
        elif review_rating == "Three":
            product_informations["review_rating"] = "3/5"
        elif review_rating == "Four":
            product_informations["review_rating"] = "4/5"
        elif review_rating == "Five":
            product_informations["review_rating"] = "5/5"
        else:
            product_informations["review_rating"] = "0/5"

        # ___ajout des informations produits transformés___
        products_informations_transformed.append(product_informations)

    return products_informations_transformed


def _create_category_dir(category):
    CAT_DIR = DATA_DIR / category
    CAT_DIR.mkdir(parents=True, exist_ok=True)
    return CAT_DIR


# _____sauegarder les images de chaque livre_____
def save_products_images(products_data):
    CAT_DIR = _create_category_dir(products_data[0].get("category"))
    IM_DIR = CAT_DIR / "images"
    IM_DIR.mkdir(exist_ok=True)
    for product_data in products_data:
        image_url = product_data.get("image_url")
        content = requests.get(image_url).content
        image_name = f"{product_data.get('title')}.jpg"
        with open(IM_DIR / image_name, "wb") as image_file:  # utilisation du mode d'ouverture "wb" pour write binary
            image_file.write(content)


# _____stocker les données dans un fichier csv_____
def save_products_informations_in_csv(products_data: list[dict]):
    CAT_DIR = _create_category_dir(products_data[0].get("category"))
    with open(f"{CAT_DIR}/{products_data[0].get("category")}.csv", "w", newline="",
              encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=products_data[0].keys(), delimiter=",")
        writer.writeheader()
        for product_data in products_data:
            writer.writerow(product_data)
    print(f"Toutes les données des livres de la catégorie '{products_data[0].get('category')}' ont étés sauvegardés...")


# _____Fonction main pour lancer l'application à partir de l'url principal du site_____
def main():
    gategories_urls = get_categories_urls(main_url)
    for category_url in gategories_urls:
        pages_urls = get_pages_urls_from_category(category_url)
        products_urls = get_products_urls_from_category(pages_urls)
        products_informations = get_products_informations(products_urls)
        products_informations_transformed = transform_products_informations(products_informations)
        save_products_images(products_informations_transformed)
        save_products_informations_in_csv(products_informations_transformed)


if __name__ == "__main__":
    main()

    # url_test = "https://books.toscrape.com/catalogue/category/books/fiction_10/index.html"
    # pages_urls = get_pages_urls_from_category(url_test)
    # products_urls = get_products_urls_from_category(pages_urls)
    # products_informations = get_products_informations(products_urls)
    # products_informations_transformed = transform_products_informations(products_informations)
    # save_products_images(products_informations_transformed)
    # save_products_informations_in_csv(products_informations_transformed)
