import re,nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# Plotting tools
import pyLDAvis
import pyLDAvis.sklearn

from config import config
import pickle

import logging
import logging.handlers as handlers
import time
import datetime

import pandas as pd
import numpy as np

class TopicAnalyser:
    def __init__(self):
        self.count=0
        try:
            self.logger=self.initLogger()
            # Load the TF model 
            filename = 'model/tf_model.pkl'
            self.tf=pickle.load(open(filename, 'rb'))

            self.count+=1

            # Load the TF Vectoriser 
            filename = 'model/tf_vect_model.pkl'
            self.tf_vectorizer=pickle.load(open(filename, 'rb'))

            self.count+=1

            self.logger.info("Topic Vectorizer Model loaded...")
            print("Topic Vectorizer Model loaded...")

            filename = 'model/lda_model.pkl'
            self.lda=pickle.load(open(filename, 'rb'))
            self.logger.info("LDA Model loaded...")
            print("LDA Model loaded...")

            self.count+=1
        except Exception as e:
            self.logger.error(e)

    def initLogger(self):
        logging.basicConfig(filename="logs/report",format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger('Training Summary')
        logger.setLevel(logging.INFO)
        return logger

    def generate(self):
        if(self.count==3):
            self.logger.info("Topic Visualisation Started...") 
            print("Topic Visualisation Started...") 
            try:
                output=pyLDAvis.sklearn.prepare(self.lda, self.tf, self.tf_vectorizer, mds='tsne')
                pyLDAvis.save_html(output, 'report/topic_output.html')
                self.logger.info("HTML output saved")
                print("HTML output saved")
            except Exception as e:
                self.logger.error(e)
                print(e)
            self.logger.info("Topic Visualisation Completed...") 
            print("Topic Visualisation Completed...")
        else:
            print("ML Models missing!!! Please run the training module.")
            self.logger.info("ML Models missing!!! Please run the training module.") 
