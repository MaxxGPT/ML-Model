import pickle

import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation

import logging
import logging.handlers as handlers
import time

class GridSearch:
    def __init__(self,tf):
        self.tf=tf
        self.search_components=[2, 3, 4]
        self.logger=self.init_logger()
        self.logger.info("init...")
    
    def init_logger(self):
        logger = logging.getLogger('GridSearch')
        logger.setLevel(logging.INFO)
        return logger

    def start(self):   
        self.logger.info("Started...")
        no_topics=4
        t = time.process_time()
        try:
            # Define Search Param
            search_params = {'n_components': self.search_components}
            # Init the Model
            lda = LatentDirichletAllocation(max_iter=5, learning_method='online', learning_offset=50.,random_state=0)
            # Init Grid Search Class
            model = GridSearchCV(lda, param_grid=search_params,verbose=10)
            # Do the Grid Search
            model.fit(self.tf)
            # Best Model
            best_lda_model = model.best_estimator_
            # Model Parameters
            self.logger.info("Completed...")
            self.logger.info(model.best_params_)
            no_topics=model.best_params_["n_components"]
        except Exception as e:
            self.logger.error(e)
        elapsed_time = time.process_time() - t
        self.logger.info("Execution Time[Seconds] "+str(elapsed_time))
        return no_topics