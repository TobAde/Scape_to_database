from pandas.core.frame import DataFrame
import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
import psycopg2.extras as extras

dotenv_paths = Path('.env')
load_dotenv(dotenv_path=dotenv_paths)

class Database:
    '''
    Pushes data from the aliexpress scraper to a postgres database
    Contains: create_category_tb(), create_products_tb(), create_tables(), drop_table(tablename), insert_category(df),
            insert_products(df), insert_data(df), select_data(keyword), to_csv(df, file_name), close()
    '''
    def __init__(self):
        self.__conn = psycopg2.connect(  
        database = os.getenv("DB"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        host=os.getenv("HOST"),
        port=os.getenv("PORT")
        )
        self.__cur = self.__conn.cursor()

    def create_category_table(self, my_df: pd.DataFrame) -> int:
        '''
        creates the category table in database if it dosn't exist and inserts item categories to the table
        :param my_df: dataframe to be loaded on database
        :return: cat_id of keyword inserted
        '''
        create_cat_table = ''' 
            CREATE TABLE IF NOT EXISTS categories(
            id serial PRIMARY KEY,
            category VARCHAR(50)
        );
        '''
        self.__cur.execute(create_cat_table)
        print('Category table created!')

        item = my_df.loc[0, 'Category']
        try:
            self.__cur.execute("INSERT INTO categories (category) VALUES (%s)", (item,))
            self.__conn.commit()
            count = self.__cur.rowcount
            print(count, f"record inserted successfully into the categories table - {item})")
        except psycopg2.errors.UniqueViolation:
            print(f'{item} already exists in the category table')
            self.__cur.execute("ROLLBACK")
            self.__conn.commit()

        self.__cur.execute("SELECT * FROM categories where category = %s", (item,))
        cat_id = self.__cur.fetchone()[0]
        return cat_id

    def create_products_table(self, cat_id: int, my_df: pd.DataFrame) -> None:
        '''
        creates the product table in the database and inserts the product information to the table
        :param cat_id: category id gotten from categories table
        :param my_df: dataframe to be loaded on database
        :return: insert completed
        '''
        create_product = '''
          CREATE TABLE IF NOT EXISTS product (
          id serial PRIMARY KEY,
          item_title varchar(10000),
          item_price varchar(255),
          item_url varchar(10000),
          item_image varchar(10000),
          cat_id INT NOT NULL

        );
        '''
        self.__cur.execute(create_product)
        print('Product table created!')

        new_df = my_df.drop('Category', axis=1)
        new_df['cat_id'] = cat_id

        #This will create a list of the dataframe
        tuples = [tuple(x) for x in new_df.to_numpy()]
        cols = ','.join(list(new_df.columns))
        insert_query = "INSERT INTO product (%s) VALUES(%%s,%%s,%%s,%%s,%%s)" % (cols)
        
        
        print('Inserting data to products table..')

        try:
            extras.execute_batch(self.__cur, insert_query, tuples)
            self.__conn.commit()
            count_query = self.__cur.execute("SELECT count(*) from product where cat_id = (%s)", (cat_id,))
            print(f'Insert completed. {count_query} records were inserted.')
        except psycopg2.DatabaseError as error:
            print("Error: %s" % error)
            self.__conn.rollback()
        return

    def create_tables(self, my_df) -> None:
        '''
        calls the create_category_table and create_products_table methods together
        :param my_df: dataframe to be loaded on database
        :return: none
        '''
        cat_id = self.create_category_table(my_df)
        self.create_products_table(cat_id, my_df)
        return

    def drop_table(self, tablename: str):
        '''
        used to drop a table in the database
        :param tablename: table to be dropped
        :return: table deleted
        '''
        drop_tb = "DROP TABLE %s;" % tablename

        try:
            self.__cur.execute(drop_tb)
            self.__conn.commit()
            print(f"{tablename} table deleted")
        except psycopg2.errors.UndefinedTable:
            self.__conn.rollback()
            print(f'{tablename} table does not exist in the database')


    def select_item(self, item: str) -> pd.DataFrame:
        '''
        fetches the item data from database
        :param item: category 
        :return: Dataframe of item data
        '''
        select_query = '''
        select category, item_title Title, item_price Price, item_url Item_url, item_image Image_url from product 
        LEFT JOIN categories on product.cat_id = categories.id
        WHERE LOWER(category) = '%s'
        ''' % (item.lower(),)
        self.__cur.execute(select_query)
        item_df = pd.DataFrame(self.__cur.fetchall(), columns= ('Category', 'Title', 'Price','Item_url', 'Image_url'))
        return item_df

    def to_csv(self, df: pd.DataFrame, file_name: str) -> None:
        '''
        saves a dataframe as csv file
        :param df: dataframe to be saved as csv file
        :param file_name: name of csv file
        :return: none
        '''
        df.to_csv(f'db_{file_name}.csv')
        print(f'db_{file_name}.csv file saved to folder')
        self.__cur.close()
        self.__conn.close()
