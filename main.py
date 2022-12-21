import requests
import csv
from bs4 import BeautifulSoup





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
#Second
def get_bookURL_from_category(category_url):
  book_url=[]
  #ici nous appelons l'url de la categorie, c'est à dire nous allons à la page de la categorie
  html_page = requests.get(category_url)
  soup = BeautifulSoup(html_page.content, 'html.parser')
  
  limit_of_pages = soup.find("li", {"class": "current"})
  array_links_subpages_category = []

  if limit_of_pages is not None:
    limit_of_pages = limit_of_pages.get_text()
    limit_of_pages = limit_of_pages.replace("\n" , "")
    limit_of_pages = limit_of_pages.strip()
    limit_of_pages = limit_of_pages.split(" ")
    limit_of_pages = int(limit_of_pages[-1])
    # example of limits "Page 1 of 2"
    # ["page", "1", "of", "2"]
    for link in range(1,limit_of_pages+1):
      subpage_url = category_url.replace("index.html", "")
      subpage_url = subpage_url + f"page-{link}.html"
      array_links_subpages_category.append(subpage_url)


  if len(array_links_subpages_category) > 0:
    for url_subcategory in array_links_subpages_category:
      content_of_subpage = requests.get(url_subcategory)
      soup = BeautifulSoup(content_of_subpage.content, 'html.parser')
      container_of_books = soup.find("ol", {"class": "row"})

      for book in container_of_books.contents:
        try:
          url_book = book.nextSibling.find("h3").find("a")["href"]
          url_book = url_book.replace("../../../", 'https://books.toscrape.com/catalogue/')
          book_url.append(url_book)
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
def generate_csv_books(array_of_books):
  file_results = open('resultados_finales.csv', 'w')
  writer = csv.writer(file_results)
  writer.writerow(list( array_of_books[0].keys()))
  for dictionary in array_of_books:
      writer.writerow(dictionary.values())
  file_results.close()

results_final = []
categories = get_category_link()
for category in categories:
  books = get_bookURL_from_category(category)
  for book in books:
    book_info = get_book_info(book)
    results_final.append(book_info)

generate_csv_books(results_final)
print("PROCESO TERMINADO")






""""
list_from_links_of_books = []

dict_of_categories = {
}
url_of_categories = get_category_link()

for url in url_of_categories:
  dict_of_categories[url] = []

for category_url in url_of_categories:
  url_of_book = get_bookURL_from_category(category_url, dict_of_categories)
  list_from_links_of_books.append(url_of_book)


new_dict_final_data = {}
for key, value in dict_of_categories.items():
  new_dict_final_data[key] = {}
  for book_url in value:
    dict_features = get_book_info(book_url)
    new_dict_final_data[key][book_url] = dict_features


print(new_dict_final_data)

"""
    

#find_next_siblings() function is used to find all the next siblings of a tag / element.
#It returns all the next siblings that match.

#En Python, una cadena de texto normalmente se escribe entre comillas dobles ("") o comillas simples (''). Para crear f-strings, solo tienes que agregar la letra f o F mayúscula antes de las comillas.

#Por ejemplo, "esto" es una cadena de texto normal y f"esto" es una f-string.




        

























