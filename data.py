from src.db import Database
from src.scraper import scrape


my_database = Database()
#sample_db.drop_table('categories')
my_database.create_tables(scrape('Bag',200))

item_bag = my_database.to_csv(my_database.select_item('bag'),'bag')




