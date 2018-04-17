import json
import networkx as nx
import operator
from networkx.algorithms.link_analysis.pagerank_alg import pagerank
from networkx.algorithms.link_analysis.hits_alg import hits

pages = json.load(open('./wikipedia/out.json', 'r'))
domain = 'https://en.wikipedia.org'
visited = {}

G = nx.Graph()

for page in pages:
    visited[page['url']] = page

for page in pages:
    for url in page['urls']:
        if u'{}{}'.format(domain, url) in visited:
            G.add_edge(page['url'], u'{}{}'.format(domain, url))


def print_result(dictionary, message):
    print message
    sorted_dict = sorted(dictionary.items(), key=operator.itemgetter(1), reverse=True)

    for rank in sorted_dict[:10]:
        print "\n", visited[rank[0]]['title'].encode('utf-8'), rank[1]
        print visited[rank[0]]['snippet']


print "\nPageRank:"

alpha = 0.85
PR = pagerank(G, alpha=alpha)
print_result(PR, "\nAlpha {}:".format(alpha))

alpha = 0.95
PR = pagerank(G, alpha=alpha)
print_result(PR, "\nAlpha {}:".format(alpha))

alpha = 0.5
PR = pagerank(G, alpha=alpha)
print_result(PR, "\nAlpha {}:".format(alpha))

alpha = 0.3
PR = pagerank(G, alpha=alpha)
print_result(PR, "\nAlpha {}:".format(alpha))


print "\nHITS:"

HITS = hits(G, max_iter=300)
hubs = HITS[0]
authorities = HITS[1]

print_result(hubs, "\nHubs:")
print_result(authorities, "\nAuthorities:")

mean = {}
for url, value in hubs.iteritems():
    mean[url] = (value + authorities[url]) / 2

print_result(mean, "\nhub and authority mean")
