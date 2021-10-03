import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape(keyword_to_scrape:str,number_of_items_to_scrape:int):
    """
        Scrapes data based on keyword and number of rows to be scrapped
    
        Parameters:
        keyword_to_search: The keyword that needs to be scrapped
        number_of_items: number of items to be scraped
    """
    category = []
    titles = []
    prices = []
    items_url = []
    images_url = []
    keyword = keyword_to_scrape.lower()
    page_url = []
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"}

    if number_of_items_to_scrape < 203 :
      page_no = 1
      print(f'Scrapping {page_no} page')
    else:
      page_no = int(round(number_of_items_to_scrape/203))
      print(f'Scrapping {page_no} pages')
      
    for i in range(1,page_no + 1):
        page_url.append('https://www.ebay.com/sch/i.html?_from=R40&_nkw=' + keyword + '&_sacat=0&_ipg=192&_pgn=' + str(i))
     # details of the information from the website
    for urls in page_url:
    
      page = ''
      while page == '':
        try:
          page = requests.get(urls)
          break
        except:
          print("Connection refused by the server..")
          print("Let me sleep for 5 seconds")
          print("ZZzzzz...")
          time.sleep(5)
          print("Was a nice sleep, now let me continue...")
          continue
      print(page.status_code)
      if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'html.parser')


        for items in soup.find_all("li", {"class":"s-item"})[2:-2]:
          if items:
              titles.append(items.select_one(".s-item__title").text)
              prices.append(items.select_one(".s-item__price").text)
              category.append(keyword_to_scrape)
              images_url.append(items.select_one(".s-item__image-img")['src']) 
              items_url.append(items.select_one(".s-item__link")["href"])
      
      else:
        print('page does not exist')

    data_dictionary ={   
            'Category':category, 
            'item_title':titles,
            'item_price':prices,
            'item_url':items_url,
            'item_image':images_url,
        }

    my_df = pd.DataFrame.from_dict(data_dictionary, orient='index')
    my_df = my_df.transpose()
    #[0:number_of_items_to_scrape]    
    
    return my_df