
from constants import BASE_URL
from bs4 import BeautifulSoup
from csv_functions import generate_csv_books
from image_functions import download_image
import os
import requests 


def get_all_categories_link():
    html_page = requests.get(BASE_URL)
    soup = BeautifulSoup(html_page.content, 'html.parser')

    links_category = soup.find('div', {'class':'side_categories'})
    links_category = links_category.find('ul', {'class':'nav nav-list'})
    links_category = links_category.find('li')
    links_category = links_category.find('ul')

    list_from_links_of_category = []
    for tag in links_category.contents:
        try:
          #url_category = BASE_URL+ "/" + tag.nextSibling.find('a')['href']
          url_category = f"{BASE_URL}/{tag.nextSibling.find('a')['href']}"

          list_from_links_of_category.append(url_category)
        except Exception as error:
          continue
    # example of result ["url_1", "url_2"...]
    return list_from_links_of_category

def nbre_pages_categorie (soup): 
  #Fonction pour determiner le nb des pages pour une catégorie  
  limit_of_pages = (soup.find("li", {"class": "current"}))

  if limit_of_pages is None:
      nb_page = 1
      return nb_page
  else:  
    nb_page = int(limit_of_pages.get_text().replace("\n" , "").strip().split(" ")[-1])
    return nb_page
 


def get_all_books_url_from_category(category_url): # simplifier cette partie 
  book_url=[]
  #ici nous appelons l'url de la categorie, c'est à dire nous allons à la page de la categorie
  html_page = requests.get(category_url)
  soup = BeautifulSoup(html_page.content, 'html.parser')
  
  
  limit_of_pages = nbre_pages_categorie(soup)
  
  array_links_subpages_category = [] #array qui prepare les url dans le cas ou il faut scraper plusieurs pages, vient de var subpage url


  if limit_of_pages is not None and limit_of_pages > 1: #cycle qui permet de trouver les page qui ne sont pas none 
    for link in range(1,limit_of_pages+1): # compte iteration 1 +1
      subpage_url = category_url.replace("index.html", "")#var subpage_url egal à category_url que nous avons deja
      subpage_url = subpage_url + f"page-{link}.html"
    array_links_subpages_category.append(subpage_url)


  if len(array_links_subpages_category) > 0: #si longueur de  l'array >0, cela contient autre page 
    for url_subcategory in array_links_subpages_category:#ycle for sur un array qui vas contenir les infos container des subpages
      content_of_subpage = requests.get(url_subcategory)#obtient code of subpage
      soup = BeautifulSoup(content_of_subpage.content, 'html.parser')# fait le parser #
      container_of_books = soup.find("ol", {"class": "row"})#ici atravers la classe row qui contient le container de books 

      for book in container_of_books.contents: #du premier livre
        try:
          url_book = book.nextSibling.find("h3").find("a")["href"]
          url_book = url_book.replace("../../../", 'https://books.toscrape.com/catalogue/')
          book_url.append(url_book)#ajoute les url a l'array book url, et les ajoute.....
        except Exception as _:
          continue
  else:
      soup = BeautifulSoup(html_page.content, 'html.parser')
      container_of_books = soup.find("ol", {"class": "row"})
      for book in container_of_books.contents:
        try:
          url_book = book.nextSibling.find("h3").find("a")["href"]
          url_book = url_book.replace("../../../", 'https://books.toscrape.com/catalogue/')
          book_url.append(url_book)
        except Exception as _:
          continue
  # naviguer dans toutes les pages de cette catégorie afin de recuperer les liens de livres
  return book_url
#quatrieme


def getpages_by_category(array_of_books):
  try:
    dict_images = {}
    books_information_file = {}

    
    distinct_categorys = [] #creation d'un array et faire cycle sur books
    for book in array_of_books:
      if book is None:
        continue
      category_name = book["category_name"] #on obtien le nom de la categorie
      distinct_categorys.append(category_name) #.append to categories
      if not os.path.isdir(f"./scrapy_information/{category_name}"): 
        os.makedirs(f"./scrapy_information/{category_name}") # si non existe creation du fichier avec le nom de la categorie
        dict_images[category_name] = [{  #iteration sur dict images pour recuperer les images au meme temps
          "image_url": book["image_url"],
          "book_name": book["title"],
          "category_name": category_name
        }]
        book.pop("image_url")#avec pop effeace image et ne peut pas contenir images car il et crée dans un fichier a part
        books_information_file[category_name] = [book] #cretion d'une categorie et lui assigne le nom du livre exemple"travel":[livre1],  
      elif os.path.isdir(f"./scrapy_information/{category_name}"):
        dict_images[category_name].append({
          "image_url": book["image_url"],
          "book_name": book["title"],
          "category_name": category_name
        })
        book.pop("image_url")
        books_information_file[category_name].append(book)
      
  
    for key , value in dict_images.items():
      file_name_books = f"./scrapy_information/{key}/books_category.csv"
      generate_csv_books(books_information_file[key], file_name_books)
      
      for image_category in value:
        image_url = image_category["image_url"]
        directory = f"scrapy_information/{key}/images_of_category"
        download_image(image_url, directory)
  except Exception as e:
    print("ERROR EN LA FUNCION getpages_by_category ")
    print(e)
    print("ERROR EN LA FUNCION getpages_by_category ")
    
    

def get_book_info(book_url):
    dict_of_features = {}
    try:
      html_page = requests.get(book_url)
      soup = BeautifulSoup(html_page.content, 'html.parser')


      title_of_book = soup.find("div", {"class": "col-sm-6 product_main"}).find("h1")
      title_of_book = title_of_book.get_text().replace("£", "")
      title_of_book = title_of_book.replace("\n", "")

      product_description = soup.find("article", {"class": "product_page"}).find("p", recursive=False).get_text()
      image_object = soup.find("div", {"class":"item active"})
      image_object_url = image_object.find("img")["src"]
      image_object_url = image_object_url.replace("../../", f"{BASE_URL}")

      category_name = soup.find("ul", {"class":"breadcrumb"}).find_all("a")[2]
      category_name = category_name.text
    

      dict_of_features["image_url"] = image_object_url
      table_of_features = soup.find("table", {"class": "table table-striped"})
      #print(table_of_features)

      rows = table_of_features.find_all("tr")
    
      for row in rows:
        cells = row.find_all("th")
        value = cells[0].get_text()
        dict_of_features[value] = row.find_all("td")[0].get_text().replace("£", "")

      dict_of_features["product_page_url"] = book_url
      dict_of_features["title"] = title_of_book
      dict_of_features["product_description"] = product_description
      dict_of_features["category_name"] = category_name
      return dict_of_features
    except Exception as e:
      #print(e)
      pass
      
 #First , j'obtients les links pour les garder dans la variable categories        

#Second, pouvoir naviguer à l'interieur des pages d'une catégorie(plsieurs pages dans ne catégorie), 
#pouvoir recuperer les infos des livres (get_book_info)
