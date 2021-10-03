from src.db import Database
from src.scraper import scrape


my_database = Database()
#my_database.drop_table('categories')
#my_database.drop_table('product')
my_database.create_tables(scrape('Bag',3000))

item_shirt = my_database.to_csv(my_database.select_item('Bag'),'Bag')




