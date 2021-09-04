import re,nltk
import spacy
import en_core_web_sm

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
            self.table_name=(config.get('DATABASE', 'TABLE'))
            self.counter+=1
            self.db=Database()
            self.counter+=1
            if(self.db.status()):
                self.logger.info("DB Connection Successful...")
                self.counter+=1
                self.db_connection=True
            else:
                self.logger.info("DB Connection Failed...")
            self.nlp = en_core_web_sm.load()
            self.remove_curly_bracket_code_pattern = re.compile(r'\{(.*?)\}')
            self.remove_url_pattern = re.compile(r'https?://\S+|www\.\S+')
            self.remove_tags_pattern = re.compile(r'(?:(?:\.vjs-|vjs-spinner|\.video-|\.ima-|\.bumpable-|video::-|@-|\*:)\S+)|(?:\bli|fff|div|body|ul\b)')
        except Exception as e:
            self.logger.error(e)

    def process_data(self):
        if(self.counter==6):
            total_records=self.db.get_table_count(self.table_name)
            self.logger.info("Total Table Size..."+str(total_records))
            # total_records=5000
            table_data=self.db.get_data(self.table_name,0,total_records)
            dataset=[]
            self.logger.info("Data Processing Started...")
            bar = Bar('Processing', max=total_records)
            for row in table_data:
                try:
                    data = row.get("content")
                    if (data is not None):
                        dataset.append(self.lemmatize_sentence(data))
                except Exception as e:
                    self.logger.error(e)
                bar.next()
            bar.finish()
            self.logger.info("Data Processing Finished...")
            self.logger.info("Processed Data Size "+str(len(dataset)))
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

    # def lemmatize_sentence(self,sentence):
    #     nltk_tagged = nltk.pos_tag(nltk.word_tokenize(sentence))
    #     wordnet_tagged = map(lambda x: (x[0], self.find_wordnet_tag(x[1])), nltk_tagged)
    #     lemmatized_sentence = []
    #     for word, tag in wordnet_tagged:
    #         if word not in self.stop_words:
    #             if tag is None:
    #                 lemmatized_sentence.append(word)
    #             else:
    #                 lemmatized_sentence.append(self.lemmatizer.lemmatize(word, tag))
    #     return " ".join(lemmatized_sentence)

    def lemmatize_sentence(self,sentence):
        sentence = sentence.replace('@font-face', '').replace('@keyframes', '')
        try:
            # Remove text within curly brackets
            sentence = self.remove_curly_bracket_code_pattern.sub("", sentence)
            # Remove urls
            sentence = self.remove_url_pattern.sub("", sentence)
            # Remove .vjs tags
            sentence = self.remove_tags_pattern.sub("", sentence)
        except Exception as e:
            self.logger.error(e)

        lemmatized_tokens = []
        for token in self.nlp(sentence):
            if not token.is_stop and not token.is_punct and not token.is_digit:
                lemmatized_tokens.append(token.lemma_.lower())
        return " ".join(lemmatized_tokens)

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
