import lemmaCache

lemmatizer_en = lemmaCache.LemmatizerEnglish()
lemmatizer_de = lemmaCache.LemmatizerGerman()

string_de = "Mein Tag war wirklich Scheiße. Ich hatte kaum Spaß und Freude. Eigentlich habe ich nur geweint."
string_en = "What the fuck are you doing? Are you doing well?"

print(string_de)
print(lemmatizer_de.lemmatize_morphys(string_de))
print(lemmatizer_de.lemmatize_spacy(string_de))
print(lemmatizer_de.lemmatize_hannover(string_de))

print()
print("******************************************************")
print()

print(string_en)
print(lemmatizer_en.lemmatize_spacy(string_en))
print(lemmatizer_en.lemmatize_nltk(string_en))


