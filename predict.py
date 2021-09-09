from text_analyser import TextAnalyser
from sentiment_analysis import SentimentAnalysis
from lda import Lda

if __name__ == "__main__":
    print("Text Analysis Started....")
    textanalyser=TextAnalyser()
    textanalyser.start()
    print("Sentiment Analysis started")
    sentiment_analysis = SentimentAnalysis()
    sentiment_analysis.start()