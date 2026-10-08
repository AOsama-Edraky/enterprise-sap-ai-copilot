"""Small BM25 index. ACL filtering precedes scoring, top-k and prompt assembly."""
import math
import re
from collections import Counter
from .security import visible, suspicious

STOP = set('a an the is are of to for in on and why how what this that can i do with it'.split())
def terms(text):
    return [t for t in re.findall(r'[a-z0-9]+', text.lower()) if t not in STOP]

class Index:
    def __init__(self, chunks):
        ids = set()
        for c in chunks:
            if (not isinstance(c, dict) or any(not isinstance(c.get(k), str) or not c[k]
                for k in ('id','tenant','title','text','version'))
                or any(not isinstance(c.get(k), list) or not c[k]
                       or any(not isinstance(v,str) or not v for v in c[k])
                       for k in ('companies','roles'))
                or c['id'] in ids):
                raise ValueError('Invalid policy chunk metadata')
            ids.add(c['id'])
        self.chunks = chunks

    def search(self, query, principal, company, k=3):
        # Corpus statistics are also scope-local: hidden documents cannot alter scores.
        allowed = [c for c in self.chunks if visible(principal, company, c)
                   and not suspicious(c['text'])]
        corpus = [Counter(terms(c['title']+' '+c['text'])) for c in allowed]
        if not corpus:
            return []
        lengths = [sum(c.values()) for c in corpus]
        avg = sum(lengths)/len(lengths) or 1
        ranked = []
        query_terms = set(terms(query))
        for chunk, counts, length in zip(allowed, corpus, lengths):
            score = 0.0
            coverage = sum(t in counts for t in query_terms)/max(1,len(query_terms))
            if coverage < 0.5:
                continue
            for term in query_terms:
                tf = counts[term]
                if not tf:
                    continue
                df = sum(term in c for c in corpus)
                idf = math.log(1+(len(corpus)-df+0.5)/(df+0.5))
                score += idf*tf*2.2/(tf+1.2*(0.25+0.75*length/avg))
            if score > 0:
                ranked.append((score, chunk))
        ranked.sort(key=lambda pair: (-pair[0], pair[1]['id']))
        return [dict(c, score=round(score, 4)) for score, c in ranked[:k]]
