import requests
import csv
from bs4 import BeautifulSoup

import os 
import shutil




main_page = 'https://books.toscrape.com/'
html_page = requests.get(main_page)
soup = BeautifulSoup(html_page.content, 'html.parser')



#Depuis la page d'accueil Recuperer les liens de categories 
   #Pour chqaue lien de cqtegorie recuperer la page de la categorie
       #pour chaque page de la categorie recuperer les liens des livres
           #pour chaque lien de livre appeler la fonction qui recupere les infos
           

# Ordre d'execution prmièrement   get_category_link , puis  get_bookURL_from_category , puis     get_book_info 
#Troisieme partie récuperer les informations du livre 
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
      image_object_url = image_object_url.replace("../../", f"{main_page}")

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
      
 #First         
def get_category_link():
    links_category = soup.find('div', {'class':'side_categories'})
    links_category = links_category.find('ul', {'class':'nav nav-list'})
    links_category = links_category.find('li')
    links_category = links_category.find('ul')

    list_from_links_of_category = []
    for tag in links_category.contents:
        try:
          #url_category = main_page+ "/" + tag.nextSibling.find('a')['href']
          url_category = f"{main_page}/{tag.nextSibling.find('a')['href']}"

          list_from_links_of_category.append(url_category)
        except Exception as error:
          continue
    # example of result ["url_1", "url_2"...]
    return list_from_links_of_category
#Second, pouvoir naviguer à l'interieur des pages d'une catégorie(plsieurs pages dans ne catégorie), 
#pouvoir recuperer les infos des livres (get_book_info)
def get_bookURL_from_category(category_url):
  book_url=[]
  #ici nous appelons l'url de la categorie, c'est à dire nous allons à la page de la categorie
  html_page = requests.get(category_url)
  soup = BeautifulSoup(html_page.content, 'html.parser')
  
  limit_of_pages = soup.find("li", {"class": "current"}) #chercher la limite of pages class current
  array_links_subpages_category = [] #array qui prepare les url dans le cas ou il faut scraper plusieurs pages, vient de var subpage url

  if limit_of_pages is not None: #cycle qui permet de trouver les page qui ne sont pas none 
    limit_of_pages = limit_of_pages.get_text()#besoin d'extraire le texte page 1 of 2, avec atribute get_text
    limit_of_pages = limit_of_pages.replace("\n" , "") #replace du saut de ligne pour rien 
    limit_of_pages = limit_of_pages.strip()#enlever les spaces grace a la fonction .strip
    limit_of_pages = limit_of_pages.split(" ")#split nous luis indicons que nous voulons separer les elements par un space
    limit_of_pages = int(limit_of_pages[-1])#la limite des pages est la position -1, dans un array -1 est le dernier element, int convertion en entier
    # example of limits "Page 1 of 2"
    # ["page", "1", "of", "2"] creation de un array le dernière element "2", car il est separé par spaces 
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
def generate_csv_books(array_of_books, file_name=None):
  if file_name is None:
    file_name  ='resultados_finales.csv'

  file_results = open(file_name, 'w')
  writer = csv.writer(file_results)
  writer.writerow(list( array_of_books[0].keys()))
  for dictionary in array_of_books:
      writer.writerow(dictionary.values())
  file_results.close()

results_final = []
categories = get_category_link()
contador = 0
for category in categories:
  #if "mystery" in category:
  books = get_bookURL_from_category(category)
  for book in books:
    book_info = get_book_info(book)
    results_final.append(book_info)


generate_csv_books(results_final)
print("PROCESO TERMINADO")
print("RESULTADOS FINALES")
print(results_final)


def getpages_by_category(array_of_books):
  dict_images = {}
  books_information_file = {}
  if os.path.isdir("./scrapy_information"):
    shutil.rmtree('./scrapy_information/')
  
  distinct_categorys = []
  for book in array_of_books:
    category_name = book["category_name"]
    distinct_categorys.append(category_name)
    if not os.path.isdir(f"./scrapy_information/{category_name}"):
      os.makedirs(f"./scrapy_information/{category_name}")
      dict_images[category_name] = [{
        "image_url": book["image_url"],
        "book_name": book["title"],
         "category_name": category_name
      }]
      book.pop("image_url")
      books_information_file[category_name] = [book]
    elif os.path.isdir(f"./scrapy_information/{category_name}"):
      dict_images[category_name].append({
        "image_url": book["image_url"],
        "book_name": book["title"],
        "category_name": category_name
      })
      book.pop("image_url")
      name_file = f"./scrapy_information/{category_name}/{category_name}_{book['UPC']}.csv"
      books_information_file[category_name].append(book)
      #generate_csv_books(, name_file)
  
  for key , value in dict_images.items():
    file_name = f"./scrapy_information/{key}/images_category_books.csv"
    file_name_books = f"./scrapy_information/{key}/books_category.csv"
    generate_csv_books(value, file_name)
    generate_csv_books(books_information_file[key], file_name_books)

  




getpages_by_category(results_final)
