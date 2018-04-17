import string
import math
from json import load

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# punkt, stopwords

stop_words = set(stopwords.words('english'))
ps = PorterStemmer()
translator = str.maketrans('', '', string.punctuation)


def normalize(text):
    tokenized = word_tokenize(text)
    cleaned = [w for w in tokenized if w not in stop_words]
    return [ps.stem(w) for w in cleaned]


data = load(open('./contest/out.json'))
titles = [normalize(t.title) for t in data]
indices = [item.id for item in data]
