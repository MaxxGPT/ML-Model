FROM python:3.7
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
RUN [ "python", "-c", "import nltk; nltk.download('all')" ]
COPY . /usr/src/app
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]