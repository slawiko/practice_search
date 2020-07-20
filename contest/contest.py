# ASOBOI-2

import string
import math
from json import load

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import RussianStemmer

import networkx as nx
from networkx.algorithms.link_analysis.pagerank_alg import pagerank


urlid = open('./KR/urlid.csv', 'r')
csv_file = urlid.readlines()
urls = {}
for row in csv_file:
    pair = row.split(",", 1)
    id, url = pair[0], pair[1][:-1]
    urls[id] = url


data = load(open('./contest/out.json'))

G = nx.Graph()

for page in data:
    for url in page['urls']:
        G.add_edge(page['url'], url)

PR = pagerank(G, alpha=0.85)

m = 0
for rank in PR.values():
    if rank > m:
        m = rank
for k, rank in PR.items():
    PR[k] = rank / m

# pr_output = open('./prs.json', 'w+')
# dump(PR, pr_output)

stop_words = set(stopwords.words('russian'))
rs = RussianStemmer()
translator = str.maketrans('', '', string.punctuation)

stop_words.add('вики')
stop_words.add('википедия')
stop_words.add('википедиа')


def normalize(text):
    text = text.translate(translator)
    tokenized = word_tokenize(text)
    cleaned = [w for w in tokenized if w not in stop_words]
    return [rs.stem(w) for w in cleaned]


titles = [normalize(item['title']) for item in data]
indices = [item['id'] for item in data]


def build_indices(indices, entities, index, rev_index):
    for i, e in zip(indices, entities):
        for term in e:
            if i not in index:
                index[i] = {term: 1}
            else:
                if term not in index[i]:
                    index[i].update({term: 1})
                else:
                    index[i][term] += 1
            if term not in rev_index:
                rev_index[term] = {i: 1}
            else:
                if i not in rev_index[term]:
                    rev_index[term].update({i: 1})
                else:
                    rev_index[term][i] += 1

index = {}
rev_index = {}

build_indices(indices, titles, index, rev_index)

rows = open('./KR/qid.csv', encoding='utf-8').readlines()
queries = []
q_indices = []
for row in rows:
    i, q = row.split(',')
    queries.append(q)
    q_indices.append(i)

queries = [normalize(q) for q in queries]


def execute_search(queries, rev_index):
    answers = []
    for query in queries:
        answer = []
        for term in query:
            if term in rev_index:
                answer.extend(list(rev_index[term].keys()))
        answers.append(list(set(answer)))
    return answers


answer_titles = execute_search(queries, rev_index)


def rsv(index, rev_index, answers, queries):
    temp_rsv = []
    b = 0.75
    k1 = 1.2
    rsvs = []
    results = []

    N = len(index)
    L_ = sum([len(f) for f in index.values()]) / N
    for answer_i, answer in answers.items():
        for doc in answer:
            m = 0
            for term in queries[answer_i]:
                if term in rev_index:
                    Nt = len(rev_index[term])
                else:
                    Nt = 0
                if term in index[doc]:
                    ftd = index[doc][term]
                else:
                    ftd = 0
                Ld = len(index[doc])
                left = math.log(1 + ((N - Nt + 0.5) / (Nt + 0.5)))
                right = (ftd * (k1 + 1)) / (k1 * (1 - b + b * Ld / L_) + ftd)
                rsv = left * right
                if rsv > m:
                    m = rsv
                temp_rsv.append(rsv)
            temp_rsv = map(lambda x: x / m, temp_rsv)
            if urls[doc] in PR:
                rsvs.append(sum(temp_rsv) * 0.9 + 0.1 * PR[urls[doc]])
            else:
                rsvs.append(sum(temp_rsv))
            temp_rsv = []
        if len(rsvs) != 0:
            _, answer = zip(*sorted(zip(rsvs, answer)))
        rsvs = []
        results.append(list(reversed(answer[-3:])))

    return results


results = []
rsvs = rsv(index, rev_index, dict(zip(q_indices, answer_titles)), dict(zip(q_indices, queries)))
for index, answer in zip(range(len(rsvs)), rsvs):
    if len(answer) < 3:
        answer.extend(['622', '17334', '15853'])
    results.append("{},{}\n".format(index, ','.join(answer[-3:])))


titles_file = open('./titles_file.txt', "w+")
titles_file.writelines(results)
