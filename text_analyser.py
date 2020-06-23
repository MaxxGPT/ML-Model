import logging
import logging.handlers as handlers
import time
import datetime

import re,nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

from config import config
import pickle
from progress.bar import Bar
from db import Database
from text_preprocessor import Preprocessor

import spacy
from collections import Counter
import en_core_web_sm

import pandas as pd
import numpy as np
import os

class TextAnalyser:

    def __init__(self):
        self.model_loaded=False
        try:

            self.logger=self.initLogger()
            self.data_chunk_size=10000
            self.logger.info("Topic Prediction Module init...")
            print("Topic Prediction Module init...")

            self.summary_table_name="prediction_summary"
        
            # Load the TF model 
            filename = 'model/tf_model.pkl'
            self.tf=pickle.load(open(filename, 'rb'))

            # Load the TF Vectoriser 
            filename = 'model/tf_vect_model.pkl'
            self.tf_vectorizer=pickle.load(open(filename, 'rb'))

            self.logger.info("Topic Vectorizer Model loaded...")
            print("Topic Vectorizer Model loaded...")

            filename = 'model/lda_model.pkl'
            self.lda=pickle.load(open(filename, 'rb'))
            self.logger.info("LDA Model loaded...")
            print("LDA Model loaded...")

            self.model_loaded=True

            self.preprocessor=Preprocessor()
            self.db=self.preprocessor.db
            self.logger.info("DB Connected...")
            print("DB Connected...")

            self.nlp = en_core_web_sm.load()
            self.logger.info("NER Module Started...")
            print("NER Module Started...")

            self.entities=os.environ['NER_ENTITIES']
            self.topics=[]
            self.topics_keywords=[]

            self.set_topics_keywords()
            self.logger.info("Topics "+str(self.topics))

        except Exception as e:
            self.logger.error(e)

    def initLogger(self):
        logging.basicConfig(filename="logs/predict",format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger('Topic Prediction')
        logger.setLevel(logging.INFO)
        return logger

    def getlastprocessed_record(self):
        last_processed_row=0
        try:
            total_records=self.db.get_table_count(self.summary_table_name)
            self.logger.info("Summary Table Size..."+str(total_records))
            print("Summary Table Size..."+str(total_records))
            skip_count=0
            if(total_records>0):
                skip_count=total_records-1
            table_data=self.db.get_data(self.summary_table_name,skip_count,total_records)
            for row in table_data:
                last_processed_row=row["last_record"]
        except Exception as e:
            self.logger.error(e)
        return last_processed_row

    def start(self):
        if(self.model_loaded):
            total_records=self.db.get_table_count(self.preprocessor.table_name)
            self.logger.info("Total Table Size..."+str(total_records))
            print("Total Table Size..."+str(total_records))
            last_processed_row=self.getlastprocessed_record()
            self.logger.info("Last processed..."+str(last_processed_row))
            print("Last processed..."+str(last_processed_row))
            #total_records=100
            table_data=self.db.get_data(self.preprocessor.table_name,last_processed_row,total_records)
            dataset=[]
            self.logger.info("Topic Prediction Started...")
            print("Topic Prediction Started...")
            bar = Bar('Processing', max=total_records)
            for row in table_data:
                try:
                    _id=row["_id"]
                    data=row["summarization"]
                    if(len(data)==0):
                        data=row["description"]
                    processed_text=self.preprocessor.lemmatize_sentence(data)
                    entity_dict=self.extract_entities(processed_text)
                    for key in entity_dict:
                        row[key]=entity_dict[key]
                    topic,topic_contribution,topic_keywords=self.predict_topic(processed_text)
                    entity_dict["Topic"]=topic
                    entity_dict["Topic_Contribution"]=topic_contribution
                    entity_dict["Tokens"]=topic_keywords
                    self.db.update_data(self.preprocessor.table_name,_id,entity_dict)
                except Exception as e:
                    self.logger.error(e)
                bar.next()
            bar.finish()
            self.logger.info("Data Processing Finished...")
            print("Data Processing Finished...")
            try:
                summary={"Last_date":datetime.datetime.now(),"last_processed_record":total_records}
                data_rows=[]
                data_rows.append(summary)
                self.db.save_data(self.summary_table_name,data_rows,False)
                self.logger.info("Summary Updated...")
                print("Summary Updated...")
            except Exception as e:
                self.logger.error(e)
        else:
            print("ML Models missing!!! Please run the training module.")
            self.logger.info("ML Models missing!!! Please run the training module.") 

    def predict_topic(self,processed_text):
        topic=""
        topic_keywords=[]
        try:
            dataset=[]
            dataset.append(processed_text)
            mytext = self.tf_vectorizer.transform(dataset)
            topic_probability_scores = self.lda.transform(mytext)
            topic=self.topics[np.argmax(topic_probability_scores)]
            topic_keywords=self.topics_keywords[np.argmax(topic_probability_scores)]
            topic_contribution=np.round(topic_probability_scores[0:,np.argmax(topic_probability_scores)][0],2)
        except Exception as e:
            self.logger.error(e)
            print(e)
        return topic,topic_contribution,topic_keywords

    def extract_entities(self,processed_text):
        try:
            doc=self.nlp(processed_text)
            entities=self.entities.split(",")
            entity_dict={}
            for entity in entities:
                entity_dict[entity]=[]
            for X in doc.ents:
                if(X.label_ in entities):
                    if(X.text not in entity_dict[X.label_]):
                        entity_dict[X.label_].append(X.text)
        except Exception as e:
            self.logger.error(e)
            print(e)
        return entity_dict

    # Create Topic Array
    def set_topics_keywords(self):
        topic_table_name="Topics"
        try:
            total_records=self.db.get_table_count(topic_table_name)
            self.logger.info("Total Table Size..."+str(total_records))
            print("Total Table Size..."+str(total_records))
            table_data=self.db.get_data(topic_table_name,0,total_records)
            for row in table_data:
                try:
                    self.topics.append(row["Topic"])
                    self.topics_keywords.append(row["Tokens"])
                except Exception as e:
                    self.logger.error(e)
                    print(e)
        except Exception as e:
            self.logger.error(e)
            print(e)
        