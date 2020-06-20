from text_preprocessor import Preprocessor
from lda import Lda

if __name__ == "__main__":
    print("Training Started....")
    preprocessor=Preprocessor()
    preprocessor.process_data()
    if(preprocessor.db_connection):
        lda=Lda(preprocessor.db)
        lda.run()
