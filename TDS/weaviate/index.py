#todo: 1.a na podstawie importÃ³w z tego pliku zainstaluj potrzebne biblioteki oraz korpus wordnet z NLTK

from datetime import datetime
from itertools import chain

import weaviate
from nltk.corpus import wordnet as wn
from nltk.corpus.reader import Synset

client = weaviate.Client("http://localhost:8080", timeout_config=(4, 60))  # or another location where your Weaviate instance is running

# funkcja pomocnicza wyciÄ…gajÄ…ca sÅ‚owa i frazy z wordnet
def words_from_synset(synset: Synset):
    return [l.name().replace('_', ' ') for l in synset.lemmas()]

#todo: 1.b stwÃ³rz schemat dla klasy fraza (Phrase) zawierajÄ…cy danÄ… frazÄ™ oraz liczbÄ™ sÅ‚Ã³w z ktÃ³rych siÄ™ skÅ‚ada
schema = {}

client.schema.delete_all()
client.schema.create(schema)

# klasa pomocnicza pozwalajÄ…ca na monitorowanie procesu indeksowania
class RequestCounter:
    count: int = 0
    time: datetime = datetime.now()

    def __call__(self, results):
        self.count += len(results)
        print(f"{len(results):10} created, {self.count:15} so far in {datetime.now() - self.time}")


with client.batch(batch_size=2048, callback=RequestCounter(), timeout_retries=8) as batch:
    wordnet = (
        lemma
        for lemma in chain.from_iterable(
        words_from_synset(synset) for synset in list(wn.all_synsets('n')))
    )

    #todo: 1.c zaindeksuj pierwsze 10 000 fraz z wordnet



# client.schema.get() # get the full schema as example