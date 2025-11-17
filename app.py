from pathlib import Path
import csv
from bs4 import BeautifulSoup
import requests

CUR_DIR = Path(__file__).resolve().parent
DATA_DIR = CUR_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

main_url = "https://books.toscrape.com"


#_____obtenir une "soup" via une requete sur un url_____
def get_soup_from_request(url):
    r = requests.get(url)
    if not r.status_code == 200:
        raise ValueError("Impossible de récupérer l'url.")
    return BeautifulSoup(r.content, "html.parser")


#_____extraction des informations_____
def get_product_informations(product_urls:list)->list[dict]:
    print(product_urls)
    products_informations = []

    for product_url in product_urls:
        soup = get_soup_from_request(product_url)

        #___url___
        product_page_url = product_url

        #___title___
        title = soup.find("h1").get_text(strip=True)

        #___category___
        breadcrumb = soup.find("ul", class_ = "breadcrumb")
        category = breadcrumb.find_all("li")[-2].get_text(strip=True)

        #___review_rating___
        rate = soup.find("p", class_="star-rating")
        review_rating = rate["class"][-1]

        #___image_url___
        image = soup.find("img")
        image_url = image["src"].replace("../..", main_url)

        #___description___
        description_header = soup.find("div", id="product_description")
        product_description = description_header.find_next("p").get_text(strip=True)

        #___product informations___
        informations = soup.find(class_ = "table table-striped")
        informations = informations.find_all("td")
        upc = informations[0].string
        price_excluding_tax = informations[2].string
        price_including_tax = informations[3].string
        number_available = informations[5].string.split()[2].strip("(")


        #___création du dict des informations___
        product_informations = {"title" : title,
                             "url" : product_page_url,
                             "category" : category,
                             "review_rating" : review_rating,
                             "image_url" : image_url,
                             "description" : product_description,
                             "upc" : upc,
                             "price_excluding_tax" : price_excluding_tax,
                             "price_including_tax" : price_including_tax,
                             "number_available" : number_available
                             }

        products_informations.append(product_informations)

    return products_informations


# _____récupérer toutes les url d'une catégorie_____
def get_products_urls_from_category(pages_urls) -> list :
    products_urls = []
    for page_url in pages_urls:
        soup = get_soup_from_request(page_url)

        #___récupérer la totalité des urls de la page dans une liste___
        products = soup.find("ol", class_ = "row")
        products = products.find_all("li")
        for product in products:
            product_url = product.find("a").get("href").replace("../../..", f"{main_url}/catalogue")
            products_urls.append(product_url)

    return products_urls



#_____ créer une liste d'url en focntion du nombre de pages d'une catégorie_____
def get_pages_urls_from_category(category_url) -> list :
    soup = get_soup_from_request(category_url)

    pages_urls = [category_url]

    # ___conditionner le changement de page en fonction du nombre de page___
    next_btn = soup.find("li", class_="next")
    if next_btn:
        next_url = next_btn.find("a").get("href")
        cat_url = category_url.split("/")
        cat_url[-1] = next_url
        next_url = "/".join(cat_url)
        pages_urls.append(next_url)
    return pages_urls


#_____récupérer la catégorie en fonction de l'url de catégorie_____
def get_category_from_url(category_url) -> str:
    soup = get_soup_from_request(category_url)
    category_name = soup.find("h1").get_text(strip=True)
    return category_name




# _____stocker les données extraites dans un fichier csv_____
def save_product_informations_in_csv(products_informations:list [dict], category_name:str):
    with open(f"{DATA_DIR}/{category_name}.csv", "w", newline="") as csvfile: #newline ="" permet d'empecher la création de ligne vide dans le fichier csv
        writer = csv.DictWriter(csvfile, fieldnames=products_informations[0].keys(), delimiter=",")
        writer.writeheader()
        for product_information in products_informations:
            writer.writerow(product_information)



if __name__ == "__main__":
    url_test = "https://books.toscrape.com/catalogue/category/books/mystery_3/page-1.html"
    pages_urls = get_pages_urls_from_category(url_test)
    category = get_category_from_url(url_test)
    products_urls = get_products_urls_from_category(pages_urls)
    product_informations = get_product_informations(products_urls)
    save_product_informations_in_csv(product_informations, category)
