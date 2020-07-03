# Topic Extraction Machine Learning Model #
Python module for analysing news articles

# Summary #
This Feature is divided into three modules . Training,Visualisation and Prediction. 

## Training ##

Core part of the application .It will pull entire table data from Mongodb for training the model.It will take some time based on the number of records in the 
articles table. But this is a one time job. No need to run this module unless there is a massive change in the table size . Everytime this module will take 
entire table data for training so use it effectively.
Steps included in the training model.

    * Text Preprocessing (Stop Words Removal,Lemmatization) 
    * Document-Word matrix Creation (CountVectorizer)	
    * Grid Search *
    * LDA *
	
This is a one time job. After successful execution of this module we can see 4 files in models folder and extracted topics in the Topics table . In this mongodb 
table we can edit the Topic name .Please do not make any changes in the Tokens column.
lda_model.pkl file is the main module for extracting topics. All other files are intermediate outputs and we can use it if required .For ex if you need preprocessed
row data take preprocessed_data.pkl and load it using pickles library. Document-Word matrix is also avalible in tf_model.pkl file. All training execution details will be
avalible in train_summary table.

### python train.py ###

## Visualisation ##

This module will generate html output of the extracted topics in the report folder. This html output is interactive and it will give quick summary of the model . 
After every successful training we need to run this module for checking the ouput of the model . 

### python report.py ###

## Prediction ##

This module scans each record in the article table and find the associated Topic,Topic contribution percentage and NER attributes and save back to the same table
as seperate columns.First time it will take some time for processing the entire dataset. Then it will take only latest records . Last processed record and date 
saved in a sepearte table called prediction_summary.

### python predict.py ###

# Configuration #

All configuration variables should be system variables.

## Database ##
	DB_USERNAME:
	DB_PASSWORD:
	DB_HOST: ""
	DB_PORT: 
	DB_NAME: ""
	SOURCE_TABLE: ""
## LDA ##
	LDA_NO_TOP_WORDS: Number of words needs to include in each topics. Recommonded value is 50
	LDA_FEATURES: Number of features needs to consider for creating topics. Recommonded value is 5000
## NER(Named Entity Recognition) ##
	NER_ENTITIES: Entities needs to extract from each documents.All entities should be seperated by commas.Each item will be available as a column in articles table. 
	Supported Entities
	TYPE		DESCRIPTION
	PERSON		People, including fictional.
	NORP		Nationalities or religious or political groups.
	FAC			Buildings, airports, highways, bridges, etc.
	ORG			Companies, agencies, institutions, etc.
	GPE			Countries, cities, states.
	LOC			Non-GPE locations, mountain ranges, bodies of water.
	PRODUCT		Objects, vehicles, foods, etc. (Not services.)
	EVENT		Named hurricanes, battles, wars, sports events, etc.
	WORK_OF_ART	Titles of books, songs, etc.
	LAW			Named documents made into laws.
	LANGUAGE	Any named language.
	DATE		Absolute or relative dates or periods.
	TIME		Times smaller than a day.
	PERCENT		Percentage, including ”%“.
	MONEY		Monetary values, including unit.
	QUANTITY	Measurements, as of weight or distance.
	ORDINAL		“first”, “second”, etc.
	CARDINAL	Numerals that do not fall under another type.

# Dependencies #

	* Python (>= 3.7)
	* scikit-learn (>=0.23.1)
	* All required libraries included in the requirements.txt file. 
	
# Testing #
	
	Run test_modules.py for testing the MongoDB connectivity.   
	
# Deployment instructions #
	
	All required steps included in the deployment_instructions.doc file.
	


