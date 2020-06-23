import re,nltk

from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords,wordnet
from nltk.stem import WordNetLemmatizer

import logging
import logging.handlers as handlers
import time

from config import config
import pickle
from progress.bar import Bar
from db import Database
import os

class Preprocessor():

    def __init__(self):
        self.counter=0
        self.db_connection=False
        try:
            self.logger=self.initLogger()
            self.counter+=1
            self.data_chunk_size=10000

            self.lemmatizer = WordNetLemmatizer()
            self.counter+=1
            self.stop_words = set(stopwords.words('english'))
            self.counter+=1
            self.logger.info("Preprocessing Started ...")
            print("Preprocessing Started ...")
            self.table_name=os.environ['SOURCE_TABLE']
            print(self.table_name)
            self.counter+=1
            self.db=Database()
            self.counter+=1
            if(self.db.status()):
                self.logger.info("DB Connection Successful...")
                print("DB Connection Successful...")
                self.counter+=1
                self.db_connection=True
            else:
                self.logger.info("DB Connection Failed...")
                print("DB Connection Failed...")
        except Exception as e:
            self.logger.error(e)
            print(e)

    def process_data(self):
        if(self.counter==6):
            total_records=self.db.get_table_count(self.table_name)
            self.logger.info("Total Table Size..."+str(total_records))
            print("Total Table Size..."+str(total_records))
            #total_records=100
            table_data=self.db.get_data(self.table_name,0,total_records)
            dataset=[]
            self.logger.info("Data Processing Started...")
            print("Data Processing Started...")
            bar = Bar('Processing', max=total_records)
            for row in table_data:
                try:
                    data=row["summarization"]
                    if(len(data)==0):
                        data=row["description"]
                    if(data is not None):    
                        dataset.append(self.lemmatize_sentence(data))
                except Exception as e:
                    self.logger.error(e)
                bar.next()
            bar.finish()
            self.logger.info("Data Processing Finished...")
            print("Data Processing Finished...")
            self.logger.info("Processed Data Size "+str(len(dataset)))
            print("Processed Data Size "+str(len(dataset)))
            filename = 'model/preprocessed_data.pkl'
            pickle.dump(dataset, open(filename, 'wb'))
        else:
            self.logger.info("DB Connection Failure .... Please check configured Database connection details")
            print("DB Connection Failure .... Please check configured Database connection details")

    def initLogger(self):
        logging.basicConfig(filename="logs/train",format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger('preprocess')
        logger.setLevel(logging.INFO)
        return logger
    
    def lemmatize_sentence(self,sentence):
        nltk_tagged = nltk.pos_tag(nltk.word_tokenize(sentence))  
        wordnet_tagged = map(lambda x: (x[0], self.find_wordnet_tag(x[1])), nltk_tagged)
        lemmatized_sentence = []
        for word, tag in wordnet_tagged:
            if word not in self.stop_words:
                if tag is None:
                    lemmatized_sentence.append(word)
                else:        
                    lemmatized_sentence.append(self.lemmatizer.lemmatize(word, tag))
        return " ".join(lemmatized_sentence)
    
    # function to check nltk tag to wordnet tag
    def find_wordnet_tag(self,nltk_tag):
        if nltk_tag.startswith('J'):
            return wordnet.ADJ
        elif nltk_tag.startswith('V'):
            return wordnet.VERB
        elif nltk_tag.startswith('N'):
            return wordnet.NOUN
        elif nltk_tag.startswith('R'):
            return wordnet.ADV
        else:          
            return None
