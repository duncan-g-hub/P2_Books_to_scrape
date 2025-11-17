from pathlib import Path
import csv
from bs4 import BeautifulSoup
import requests

CUR_DIR = Path(__file__).resolve().parent
DATA_DIR = CUR_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

main_url = "https://books.toscrape.com"


#_____extraction des informations_____
def extract_book_informations(url):
    r = requests.get(url)
    if not r.status_code == 200:
      raise ValueError("Impossible de récupérer l'url.")

    soup = BeautifulSoup(r.content, "html.parser")

    #___url___
    product_page_url = url

    #___title___
    title = soup.find("h1").string

    #___category___
    breadcrumb = soup.find("ul", class_ = "breadcrumb")
    category = breadcrumb.find_all("li")[-2].get_text().strip()

    #___review_rating___
    rate = soup.find("p", class_="star-rating")
    review_rating = rate["class"][-1]

    #___image_url___
    image = soup.find("img")
    image_url = image["src"].replace("../..", main_url)

    #___description___
    description_header = soup.find("div", id="product_description")
    product_description = description_header.find_next("p").string

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


# _____stocker les données extraites dans un fichier csv_____
def save_book_informations_in_csv(book_informations):
    with open(f"{DATA_DIR}/{book_informations['title']}.csv", "w", newline="") as csvfile: #newline ="" permet d'empecher la création de ligne vide dans le fichier csv
        writer = csv.DictWriter(csvfile, fieldnames=book_informations.keys())
        writer.writeheader()
        writer.writerow(book_informations)


if __name__ == "__main__":
    url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    # extract_book_informations(url)
    save_book_informations_in_csv(extract_book_informations(url))