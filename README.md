# AWT-Project

## Getting started
Run the following in root folder to start the system:

- `docker-compose up --build` Build Server and then start Neo4J Database and Server
- `curl -X POST http://localhost:5000/competencies/initialize` Initialize the Database and Store (takes around 5 Minutes) or
- Go to `http://localhost:5000/api/docs` and execute the "Initialize" Endpoint for Competencies


## Development
Use the following commands for development (in the root folder):
1. Create a `.env` file
2. Paste (and adjust if necessary) the following content into the `.env` file: 
```
DB_URI=bolt://localhost:7687
DATA_FILE=./data/skills_de.csv
MODEL_FILES=./data/MLmodel
```
3. `docker-compose up db` to only start Neo4J Database
4. `pipenv install` to install requirements
5. `pipenv run python -m flask run` to start the server (for Dev/Debug purposes)
6. `curl -X POST http://localhost:5000/competencies/initialize` to initialize the Database and Store (takes around 5 Minutes)

### Clean up Database
1. `match (a) -[r] -> () delete a, r` to clean up relations
2. `match (a) delete a` to clean up nodes

## Documentation of API
You can find the documentation of our API at `http://localhost:5000/api/docs` once you have the system up and running.

## Preprocessing
To use the preprocessing pipeline use the following code:
```
from app.preprocessing_utils import PreprocessorGerman
prc_pipeline = PreprocessorGerman()
preprocessed_course_descriptions = prc_pipeline.preprocess_course_descriptions(course_descriptions)
```

## Machine Learning
To use the trained Entity Recognition Model use the following code:
```
import spacy
    
# load model
nlp = spacy.load(path_to_model)
# pass a preprocessed course description to the model
doc = nlp()
# retrieve the entities
ents = doc.ents
```
