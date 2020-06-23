from pymongo import MongoClient
from config import config

import logging
import logging.handlers as handlers
import time
import os

class Database:
    def __init__(self):
        self.db_username = os.environ['DB_USERNAME']
        self.db_password = os.environ['DB_PASSWORD']
        self.db_host = os.environ['DB_HOST']
        self.db_port = os.environ['DB_PORT']
        self.db_name = os.environ['DB_NAME']

        self.logger=self.init_logger()
        self.logger.info("DB Connection init...")
        print("DB Connection init...")
        self.client=self.connect()
    
    def status(self):
        if(self.client):
            return True
        else:
            return False

    def init_logger(self):
        logger = logging.getLogger('database')
        logger.setLevel(logging.INFO)
        return logger

    def connect(self):
        if(self.db_username!="NA"):
            client = MongoClient(self.db_host+":"+self.db_port, username=self.db_username,password=self.db_password)
        else:
            client = MongoClient(self.db_host+":"+self.db_port)
        return client

    def get_table_count(self,db_table):
        dbclient=self.client[self.db_name]
        table_ref=dbclient[db_table]
        total_records=table_ref.find().count()
        return total_records

    def get_data(self,db_table,start_record,end_record):
        dbclient=self.client[self.db_name]
        table_ref=dbclient[db_table]
        myresult=None
        if(start_record>0):
            myresult = table_ref.find().skip(start_record).limit(end_record)
        else:    
            myresult = table_ref.find().limit(end_record)
        return myresult

    def save_data(self,db_table,mylist,flush):
        dbclient=self.client[self.db_name]
        table_ref=dbclient[db_table]
        if(flush):
            table_ref.remove( { } )
        documents = table_ref.insert_many(mylist)
    
    def update_data(self,db_table,document_id,new_columns):
        dbclient=self.client[self.db_name]
        dbclient[db_table].find_one_and_update( {'_id': document_id}, {'$set': new_columns})


