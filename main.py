import requests
from bs4 import BeautifulSoup
html_page = requests.get('https://books.toscrape.com/')
soup = BeautifulSoup(html_page.content, 'html.parser')

soup.prettify #get the web page nicer

#Scrape de un seul livre, dans une première page de liste de livres
soup.find_all('li', {'class':'col-xs-6 col-sm-4 col-md-3 col-lg-3'})
first_20 = soup.find_all('li', {'class':'col-xs-6 col-sm-4 col-md-3 col-lg-3'})
len(first_20)
#choisir un livre dans la liste
first = first_20[0]
#trouver : url, price, image, stock, titre, rating
first.find('a')['href'] #url
first.find('h3').find('a')['title'] #title
first.find('p',class_='price_color').text #prix
first.find('p',class_='instock availability').text #stock
first.find_all('p',{'class':'star-rating Three'}) # rating
import re
regex = re.compile("star-rating (.*)")
first.find ('p', {'class': regex})
first.find ('p', {'class': regex})['class'][-1] #nombre de star
#print(first)

#store each book information into a dictionary (with keys)mettre tout l'information dans un dictionnaire
def clean_scrape(book): 
    info = {} #dictionnaire
    
    info['title'] = book.find('h3').find('a')['title'] #creation of new keys here title
    info['price'] = book.find('p',class_='price_color').text #creation of new keys here price
    
    if 'In stock' in first.find('p',class_='instock availability').text: #creation of new keys here in stock
        info['in_stock'] = True #here i used true or false to erase spaces + letters annd '\n\n    \n        In stock\n    \n'
    else:
        info['in_stock'] = False
        
    info['stars'] = book.find ('p', {'class': regex})['class'][-1] #creation of new keys here stars
    info['url'] = 'https://books.toscrape.com/'+ book.find('a')['href'] #creation of new keys here url
    
    return info
#print(clean_scrape(first)) #test get a dictionary clean_scrape

books_dicts = [clean_scrape(book) for book in first_20]
#print(books_dicts)

#Scraping multiples pages (pagination)
url = 'https://books.toscrape.com/catalogue/page-1.html'
urls = ['https://books.toscrape.com/catalogue/page-{}.html'.format(i) for i in range (1, 51)]
urls #get the list of urls

#cette fonction prends 20 livres pour chacun des URL et parse a travers la liste des urls pour obtenir toute l'information des livres du site
def get_20_books (url): 
    
    html_page = requests.get(url)
    soup = BeautifulSoup(html_page.content, 'html.parser')
    
    raw = soup.find_all('li',{'class': 'col-xs-6 col-sm-4 col-md-3 col-lg-3'})
    to_dicts = [clean_scrape(book) for book in raw]
    return to_dicts

#test avec une page 43
get_20_books('https://books.toscrape.com/catalogue/page-43.html')

#creation d'une list et mettre toute l'info des dictionnaires, avec .extend 

all_dicts = []

for url in urls:
    all_dicts.extend(get_20_books(url))
    
print(len(all_dicts)) 
all_dicts





        

























