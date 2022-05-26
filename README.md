# AWT-Project

## Getting started
Run the following in root folder

- `pipenv install` to install requirements
- `pipenv run python -m flask run` to start the server (for Dev/Debug purposes)
- `docker-compose up` Start Neo4J Database and Server
- `docker-compose up --build` Rebuild Server and then start Neo4J Database and Server
- `docker-compose start db` Only start Neo4J Database
- `pipenv run python -m spacy download de_core_news_sm` To download german spaCy Data
## API server
You can find the documentation of our API [here](https://amir-mo1999.github.io/AWT-Project/).