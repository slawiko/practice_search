import string
import math

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# punkt, stopwords

stop_words = set(stopwords.words('english'))
ps = PorterStemmer()
translator = str.maketrans('', '', string.punctuation)


def parse(file):
    INDEX_SYMBOL = '.I'
    TITLE_SYMBOL = '.T'
    ABSTRACT_SYMBOL = '.W'
    AUTHOR_SYMBOL = '.A'
    SMTH_SYMBOL = '.B'

    raw_data = file.readlines()

    in_title = False
    in_abstract = False

    title = []
    abstract = []

    indices = []
    titles = []
    abstracts = []

    for line in raw_data:
        if INDEX_SYMBOL in line:
            indices.append(line[3:][:-1])
            if in_title:
                titles.append(' '.join(title))
                title = []
            if in_abstract:
                abstracts.append(' '.join(abstract))
                abstract = []
            in_title = False
            in_abstract = False
            continue
        if TITLE_SYMBOL in line:
            if in_abstract:
                abstracts.append(' '.join(abstract))
                abstract = []
            in_title = True
            in_abstract = False
            continue
        if ABSTRACT_SYMBOL in line:
            if in_title:
                titles.append(' '.join(title))
                title = []
            in_abstract = True
            in_title = False
            continue
        if AUTHOR_SYMBOL in line or SMTH_SYMBOL in line:
            if in_title:
                titles.append(' '.join(title))
                title = []
            if in_abstract:
                abstracts.append(' '.join(abstract))
                abstract = []
            in_title = False
            in_abstract = False
            continue
        if in_title:
            title.append(line)
            continue
        if in_abstract:
            abstract.append(line)
            continue

    if in_title:
        titles.append(' '.join(title))
    if in_abstract:
        abstracts.append(' '.join(abstract))

    return indices, titles, abstracts


def normalize(text):
    tokenized = word_tokenize(text)
    cleaned = [w for w in tokenized if w not in stop_words]
    return [ps.stem(w) for w in cleaned]


data = open('./data/cran.all.1400')
indices, titles, abstracts = parse(data)
titles = [normalize(t) for t in titles]
abstracts = [normalize(t) for t in abstracts]


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


title_index = {}
title_rev_index = {}
build_indices(indices, titles, title_index, title_rev_index)

abstract_index = {}
abstract_rev_index = {}
build_indices(indices, abstracts, abstract_index, abstract_rev_index)

query_file = open('./data/cran.qry')

q_indices, _, queries = parse(query_file)
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


answer_abstracts = execute_search(queries, abstract_rev_index)
answer_titles = execute_search(queries, title_rev_index)


def rsv(index, rev_index, answers, queries):
    temp_results = []
    b = 0.75
    k1 = 1.2
    rsvs = []
    results = []

    N = len(index)
    L_ = sum([len(f) for f in index.values()]) / N
    for answer_i, answer in answers.items():
        for doc in answer:
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
                # left = math.log(N / Nt)
                right = (ftd * (k1 + 1)) / (k1 * (1 - b + b * Ld / L_) + ftd)
                temp_results.append(left * right)
            rsvs.append(sum(temp_results))
            temp_results = []
        _, answer = zip(*sorted(zip(rsvs, answer)))
        rsvs = []
        results.append(list(reversed(answer[-10:])))

    return results


results = []
rsvs = rsv(title_index, title_rev_index, dict(zip(q_indices, answer_titles)), dict(zip(q_indices, queries)))
for index, answer in zip(range(len(rsvs)), rsvs):
    for doc in answer:
        results.append("{} {}\n".format(index + 1, doc))
titles_file = open('./titles_file.txt', "w+")
titles_file.writelines(results)

results = []
rsvs = rsv(abstract_index, abstract_rev_index, dict(zip(q_indices, answer_abstracts)),
           dict(zip(q_indices, queries)))
for index, answer in zip(range(len(rsvs)), rsvs):
    for doc in answer:
        results.append("{} {}\n".format(index + 1, doc))
abstracts_file = open('./abstracts_file.txt', "w+")
abstracts_file.writelines(results)
