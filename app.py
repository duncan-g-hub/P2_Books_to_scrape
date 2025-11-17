from pathlib import Path
import csv
from bs4 import BeautifulSoup
import requests

CUR_DIR = Path(__file__).resolve().parent
DATA_DIR = CUR_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

main_url = "https://books.toscrape.com"


#_____extraction des informations_____
def extract_book_informations(product_url:str)->dict:
    r = requests.get(product_url)
    if not r.status_code == 200:
      raise ValueError("Impossible de récupérer l'url.")

    soup = BeautifulSoup(r.content, "html.parser")

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


    #___créatioon du dict des informations___
    book_informations = {"title" : title,
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

    return book_informations





# _____récupérer toutes les url d'une catégorie_____
def get_books_urls_from_category(pages_urls) -> list :
    books_urls = []
    for page in pages_urls:
        r = requests.get(page)
        if not r.status_code == 200:
            raise ValueError("Impossible de récupérer l'url.")
        soup = BeautifulSoup(r.content, "html.parser")

        #___récupérer la totalité des urls de la page dans une liste___
        books = soup.find("ol", class_ = "row")
        books = books.find_all("li")
        for book in books:
            book_url = book.find("a").get("href").replace("../../..", main_url)
            books_urls.append(book_url)

    return books_urls



#_____ créer une liste d'url en focntion du nombre de page d'une catégorie_____
def get_pages_urls_from_category(category_url) -> list :
    r = requests.get(category_url)
    if not r.status_code == 200:
        raise ValueError("Impossible de récupérer l'url.")

    soup = BeautifulSoup(r.content, "html.parser")
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


# _____stocker les données extraites dans un fichier csv_____
def save_book_informations_in_csv(book_informations:dict):
    with open(f"{DATA_DIR}/{book_informations['title']}.csv", "w", newline="") as csvfile: #newline ="" permet d'empecher la création de ligne vide dans le fichier csv
        writer = csv.DictWriter(csvfile, fieldnames=book_informations.keys(), delimiter=",")
        writer.writeheader()
        writer.writerow(book_informations)



if __name__ == "__main__":
    url = "https://books.toscrape.com/catalogue/category/books/religion_12/index.html"
    get_books_urls_from_category(get_pages_urls_from_category(url))