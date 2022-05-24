import requests


class Store:
    baseUrl = "https://ec.europa.eu/esco/api"

    def __init__(self, language="de"):
        self.language = language

    def check_term(self, term):
        query = {"text": term, "language": self.language}
        response = requests.get(self.baseUrl + "/terms", params=query)
        json = response.json()
        return json["total"] > 0

    def check_sequence(self, sequence):
        query = {"text": sequence, "language": self.language}
        response = requests.get(self.baseUrl + "/suggest2", params=query)
        json = response.json()
        return json["_embedded"]["results"]
