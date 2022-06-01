# AWT-Project

## Getting started
Run the following in root folder

- `pipenv install` to install requirements
- `pipenv run python -m flask run` to start the server (for Dev/Debug purposes)
- `docker-compose up` Start Neo4J Database and Server
- `curl -X POST http://localhost:5000/initialize` to initiliaze the Database and Store (takes around 10 Minutes)
- `docker-compose up --build` Rebuild Server and then start Neo4J Database and Server
- `docker-compose start db` Only start Neo4J Database
- `pipenv run python -m spacy download de_core_news_sm` To download german spaCy Data
- `pipenv run python -m spacy download en_core_web_sm` To download english spaCy Data
## API server
You can find the documentation of our API [here](https://amir-mo1999.github.io/AWT-Project/).

## Pre-processing
To use the pre-processing pipeline use the following code:
```
from app.text_processing_utils import TextProcessorGerman
prc_pipeline = TextProcessorGerman()
pre_processed_course_descriptions = prc_pipeline.preprocess_course_descriptions(course_descriptions)
```
