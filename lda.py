import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

import pandas as pd
import numpy as np
import os

import logging
import logging.handlers as handlers
import time
import datetime
from gridsearch import GridSearch
from config import config
from db import Database

class Lda:
    def __init__(self,db):

        filename = 'model/preprocessed_data.pkl'
        self.dataset=pickle.load(open(filename, 'rb'))
        self.logger=self.init_logger()
        self.logger.info("Preprocessed Data Loaded....")
        self.logger.info("data size "+str(len(self.dataset)))
        self.no_features=int(os.environ['LDA_FEATURES'])
        self.summary_table_name="train_summary"
        self.n_words=int(os.environ['LDA_NO_TOP_WORDS'])
        self.no_topics=4
        self.tf_vectorizer=None
        self.tf=None
        self.lda = None
        self.db=db
        self.target_table_name="Topics"
    
    def init_logger(self):
        logger = logging.getLogger('LDA')
        logger.setLevel(logging.INFO)
        return logger

    def run(self):   
        t = time.process_time()
        try:

            self.tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=self.no_features, stop_words='english',
                                strip_accents='ascii',analyzer = 'word',token_pattern='[a-zA-Z]{3,}')
            self.tf =self.tf_vectorizer.fit_transform(self.dataset)

            self.logger.info("Count Vectorizer Done")
            print("Count Vectorizer Done")

            # save the model to disk
            filename = 'model/tf_model.pkl'
            pickle.dump(self.tf, open(filename, 'wb'))

            # save the model to disk
            filename = 'model/tf_vect_model.pkl'
            pickle.dump(self.tf_vectorizer, open(filename, 'wb'))

            gridsearch=GridSearch(self.tf)

            self.no_topics = gridsearch.start()

            self.logger.info("Training Started")
            print("Training Started")

            self.lda =  LatentDirichletAllocation(n_components=self.no_topics, max_iter=5, 
                learning_method='online', learning_offset=50.,random_state=0).fit(self.tf)

            self.logger.info("Training Completed")
            print("Training Completed")

            # save the model to disk
            filename = 'model/lda_model.pkl'
            pickle.dump(self.lda, open(filename, 'wb'))

            self.logger.info("Model Saved")
            print("LDA Model Saved")

            self.save_topics()

            self.logger.info("Extracted Topics Pushed to Database")
            print("Extracted Topics Pushed to Database")

        except Exception as e:
            self.logger.error(e)
            print(e)

        elapsed_time = time.process_time() - t

        try:
            summary={"train_date":datetime.datetime.now(),
                        "processed_records":len(self.dataset),
                        "topic_count":self.no_topics,
                        "processing_time":elapsed_time}
            data_rows=[]
            data_rows.append(summary)
            self.db.save_data(self.summary_table_name,data_rows,False)
            self.logger.info("Training Summary Updated...")
            print("Training Summary Updated...")
        except Exception as e:
            self.logger.error(e)
            print(e)

    def save_topics(self):
        try:
            feature_names = self.tf_vectorizer.get_feature_names()
            keywords = np.array(feature_names)
            count=0
            data_rows=[]
            for topic_weights in self.lda.components_:
                top_keyword_locs = (-topic_weights).argsort()[:self.n_words]
                data_dict={"Topic":"Topic "+str(count),"Tokens":keywords.take(top_keyword_locs).tolist()}
                data_rows.append(data_dict)
                count+=1
            self.logger.info("Topics Extracted From Model ")
            print("Topics Extracted From Model ")
            self.logger.info(data_rows)
            self.db.save_data(self.target_table_name,data_rows,True)
        except Exception as e:
            self.logger.error(e)
            print(e)










