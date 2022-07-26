# AWT-Project

## Getting started

Run the following in root folder to start the system:

- `docker-compose up --build` Build Server and then start Neo4J Database and Server
- `curl -X POST http://localhost:5000/competencies/initialize` Initialize the Database and Store (takes around 5 Minutes) or
- Go to `http://localhost:5000/api/docs` and execute the "Initialize" Endpoint for Competencies

## Set up the pre-commit hook

If you haven't already run `pipenv install` and then run

- `pre-commit install`

The first time you commit something it will take a little longer to initialize the dependencies but usually the pre-commit hook only checks the diff, so it should be fast.

## Development

Use the following commands for development (in the root folder):

1. Create a `.env` file
2. Paste (and adjust if necessary) the following content into the `.env` file:

```
DB_URI=bolt://localhost:7687
DATA_FILE=./data/skills_de.csv
COURSES_FILE=./data/courses_preprocessed.csv
MODEL_FILES=./data/MLmodel
NLTK_FILES=./data/lemma_cache_data/nltk_data
MORPHYS_FILE=./data/lemma_cache_data/morphys.csv
STOPWORDS_FILE=./data/lemma_cache_data/stopwords-de.txt
ML_DIR=./ML/
```

3. `docker-compose up db` to only start Neo4J Database
4. `pipenv install` to install requirements
5. `pipenv run python -m flask run` to start the server (for Dev/Debug purposes)
6. `curl -X POST http://localhost:5000/competencies/initialize` to initialize the Database and Store (takes around 5 Minutes)

### Clean up Database

1. `match (a) -[r] -> () delete a, r` to clean up relations
2. `match (a) delete a` to clean up nodes

### Train Machine Learning Competency Extractor
Use the following commands to reproduce the Machine Learning model used in the Machine Learning based 
Competency Extractor:

1. `pipenv run python app/machine_learning.py`  this creates the spacy files for training and testing the model
2. `cd ML`  navigate the console to the "ML" directory
3. `pipenv run python -m spacy train config.cfg --output ./output` train and test the model with the created 
spacy files

## Documentation of API

You can find the documentation of our API at `http://localhost:5000/api/docs` once you have the system up and running.

## Generate HTML Documentation of the Project

1. `pipenv install` to install required dependencies
2. `pipenv run make html` to generate HTML documentation based on the current Source Code

You will find the generated HTML Documentation afterwards in the `build/html` Folder. Just drag and drop the `index.html` File 
into a Browser to start browsing the Documentation.

## Preprocessing

To use the preprocessing pipeline use the following code:

```
from app.preprocessing_utils import PreprocessorGerman
prc_pipeline = PreprocessorGerman()
preprocessed_course_descriptions = prc_pipeline.preprocess_course_descriptions(course_descriptions)
```

## Permission troubleshooting

If the data folder doesn't show up or cannot be opened try `sudo chmod a+r data -R`.

## Machine Learning

To use the trained Entity Recognition Model use the following code:

```

import spacy

nlp = spacy.load(path_to_model)

doc = nlp()

ents = doc.ents

```
