from bs4 import BeautifulSoup
import requests


#extraire des données via requests bs4 ; utiliser les balises html
#données d'un produit

main_url = "https://books.toscrape.com"

def extract_book_informations(url):
    r = requests.get(url)
    if not r.status_code == 200:
      raise ValueError("Impossible de récupérer l'url.")

    soup = BeautifulSoup(r.content, "html.parser")


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








# stocker les données extraites dabs un fichier csv



if __name__ == "__main__":
    url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    extract_book_informations(url)