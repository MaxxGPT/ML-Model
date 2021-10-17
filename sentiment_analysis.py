import datetime
import logging
import time, os
from time import perf_counter

from progress.bar import Bar
from transformers import pipeline

from config import config
from text_preprocessor import Preprocessor


class SentimentAnalysis:
    def __init__(self):
        try:
            self.logger = self.initLogger()

            self.preprocessor = Preprocessor()
            self.db = self.preprocessor.db
            self.logger.info("DB Connected...")
            self.table_name = (config.get('DATABASE', 'TABLE'))
            self.summary_table_name = "sentiment_analysis_summary"

            self.sentiment_analysis = pipeline("sentiment-analysis", model = "ProsusAI/finbert")
            self.logger.info("Loaded sentiment analysis model...")

        except Exception as e:
            self.logger.error(e)

    def initLogger(self):
        logging.basicConfig(filename="logs/sentiment-analysis",format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger('sentiment-analysis')
        logger.setLevel(logging.INFO)
        return logger

    def start(self):
        if self.sentiment_analysis:
            process_start = time.process_time()
            self.logger.info("Sentiment Analysis Started...")
            total_records = self.db.get_table_count(self.table_name)
            # total_records=5000
            self.logger.info("Total Table Size..." + str(total_records))
            table_data = self.db.get_data(self.table_name, 0, total_records)
            bar = Bar('Processing', max = total_records)
            label_count_dict = {}
            count = 0
            for row in table_data:
                try:
                    sentiment_dict= {}
                    _id = row["_id"]

                    # Determine sentiment from description
                    start = perf_counter()
                    description_sentiment = None
                    description_sentiment_score = 0
                    data = self.get_valid_data(row)
                    if data:
                        result = self.sentiment_analysis(data, truncation = True)
                        description_sentiment = result[0].get('label')
                        description_sentiment_score = result[0].get('score')
                    sentiment_dict['sentiment'] = description_sentiment
                    sentiment_dict['sentiment_score'] = description_sentiment_score
                    sentiment_dict['sentiment_time'] = perf_counter() - start
                    self.update_label_count_dict(str(description_sentiment), label_count_dict)

                    self.db.update_data(self.table_name, _id, sentiment_dict)
                    count += 1
                    self.logger.info(f'Completed {count} out of {total_records}')
                except Exception as e:
                    self.logger.error(e)
                bar.next()
            bar.finish()
            elapsed_time = time.process_time() - process_start
            self.save_summary(elapsed_time, total_records, label_count_dict)
            self.logger.info("Sentiment Analysis Completed...")
        else:
            print("Could not load sentiment analysis model!")
            self.logger.info("Could not load sentiment analysis model!")

    def get_valid_data(self, row):
        # Try getting text from: description OR summarization OR content OR title
        data = row.get("description")
        if (data is None) or len(data) < 5:
            data = row.get("summarization")
        if (data is None) or len(data) < 5:
            data = row.get("content")
        if (data is None) or len(data) < 5:
            data = row.get("title")
        return data

    def update_label_count_dict(self, label, label_count_dict):
        try:
            label_count_dict[label] = label_count_dict.get(label, 0) + 1
        except Exception as e:
            self.logger.error(e)

    def save_summary(self, elapsed_time, total_records, label_count_dict):
        try:
            summary = {
                "analysis_date": datetime.datetime.now(),
                "processed_records": total_records,
                "label_count_dict": label_count_dict,
                "processing_time": elapsed_time
            }
            data_rows = []
            data_rows.append(summary)
            self.db.save_data(self.summary_table_name, data_rows, False)
            self.logger.info("Sentiment Analysis Summary Updated...")
        except Exception as e:
            self.logger.error(e)
