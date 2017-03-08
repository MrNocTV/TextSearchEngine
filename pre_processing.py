import re
import math
import operator
import string
import time
from collections import Counter

###############################################
###############################################
##### Preprocessing ###########################
N = 1000

PUNCTUATIONS = {
    "'", ":", ",", "_",
    "!", "-", "(", ")", "[", 
    "]", "<", ">", ";", "`", 
    "{", "}", ".", "?", '"',
    "/", "\\", '“', '”', '&', 
    '@', '#', '*', '·', '=', '.', '^', '$', " ", "…", "–"
}
word_bag = {}
stop_words = []
with open('/home/loctv/IR/InformationRetrieval/IR/stop_words.txt', 'r', encoding='utf8', errors='ignore') as f:
    for token in f.readlines():
        token = token.strip()
        stop_words.append(token)

def progress(count, total, suffix=''):
    """
        print a progessbar in terminal while processing docs and indexing terms
    """
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()  # As suggested by Rom Ruben

def remove_punctutations(token):
    if token in PUNCTUATIONS:
        return ''
  
    if token[0] in PUNCTUATIONS:
        token = token[1:]
    while len(token) > 0 and token[-1] in PUNCTUATIONS:
        token = token[:-1]
    while len(token) > 0 and token[0] in PUNCTUATIONS:
        token = token[1:]
    if re.fullmatch(r'\d+', token):
        return ""
    try:
        f = float(token)
        return ""
    except Exception:
        pass
    return token.lower()

def tokenize(doc, doc_id):
    # remove speical entities 
    doc = re.sub(r'&amp;', ' ', doc)
    doc = re.sub(r'&lt; ', '', doc)
    doc = re.sub(r'\n', ' ', doc)
    doc = re.sub(r' +', ' ', doc)
    # split by space 
    tokens = doc.strip().split()
    length = 0
    freq = Counter()
    for token in tokens:
        t = token 
        token = remove_punctutations(token.strip())
        token = token.strip()
        if len(token) > 1:
            freq[token] += 1
            length += 1
    for token in freq:
        if token in word_bag:
            word_bag[token].append((doc_id,freq[token]))
        else:
            word_bag[token] = [(doc_id,freq[token])]
    # print(word_bag)
    return doc, length

#################################################
#################################################
################....#########....################
###############......#######......###############
#############..........###..........#############
###########.............#.............###########
#################################################
#################################################
#################################################
######### adding terms, docs to database ########
#################################################
#################################################
#################################################

import sys, os, django
sys.path.append("/home/loctv/InformationRetrieval") #here store is root folder(means parent).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "InformationRetrieval.settings")
django.setup()
from IR.models import Doc, Term, Entry

#############################################
#############################################
###### Indexing #############################

def dump_docs_to_database(dataset):
    doc_id = 1
    failed = 0
    try:
        for file in os.listdir(dataset):
            with open(os.path.join(dataset, file), 'r', encoding='utf16', errors='ignore') as f:
                content, length = tokenize(f.read(), doc_id)
                d_obj = Doc(id=doc_id, content=content, length=length)
                d_obj.save()
                doc_id += 1
            if doc_id == N+1:
                break
    except (UnicodeError, Exception) as e:
        failed += 1
        print(e)

def dump_terms_to_database():
    # then with each term in word_bag 
    start = time.time()
    for id, term in enumerate(word_bag):
        # create a new term 
        # print(term, word_bag[term])
        t = Term(id=id, content=term, how_many=len(word_bag[term]), idf=(1+math.log(N/len(word_bag[term]))))
        t.save()
        # then with each tearm, get how many docs that contains it as well term's frequency
        # term frequency later then will be normalized 
        for entry in word_bag[term]:
            e = Entry(term=t, tf=entry[1], doc=entry[0])
            e.save()
            t.entry_set.add(e)
        progress(id, len(word_bag))
    end = time.time()
    print("Took %d (s)" % round(end-start)) 
    
def clean_database():
    # remove all records in three table
    # just for testing 
    Doc.objects.all().delete()
    Term.objects.all().delete()
    Entry.objects.all().delete()

# clean_database()
# dump_docs_to_database('/home/loctv/IR/InformationRetrieval/IR/dataset')
# dump_terms_to_database()

#############################################
#############################################
###### Retrieval ############################
search_queries = (
    "Arsenal vào bán kết",
    "Nhạc sĩ Thanh Tùng", 
    "thi trượt ĐH",
    "tác hại của chất độc da cam",
    "chuyển nhượng bóng đá",
    "khám chữa bệnh BHYT"
)

def retrieval(query):
    # # calculate vector space model for query
    tmp = [remove_punctutations(x.strip().lower()) for x in query.split()]
    query_vsm = {}
    # calculate query length so that we can normalize all terms in the query
    length_query = set()
    for t in Term.objects.all():
        if t.content in tmp:
            length_query.add(t.content)
    query = [x for x in tmp if x in length_query]
    # # with each term in query, 
    for t in Term.objects.all():
        if t.content in tmp and t.content not in query_vsm:
            # normalize
            tf = tmp.count(t.content) / len(length_query)
            idf = t.idf
            # print(t.content, tf, idf)
            query_vsm[t.content] = tf*idf
    query_vsm['length'] = sum([query_vsm[x]**2 for x in query_vsm])

    # # calculate vector space model for docs 
    # # Note: docs will contains terms that are in query
    docs_vsm = {}
    # with each term in query
    for term in query_vsm:
        # if it is in database (valid)
        t = Term.objects.filter(content=term)
        if t:
            # with each entry
            for entry in t[0].entry_set.all():
                # find the doc that contains the term 
                d = Doc.objects.filter(id=entry.doc)
                # normalize the term 
                tf = entry.tf / d[0].length
                idf = t[0].idf
                # add to docs vector space model 
                if entry.doc in docs_vsm:
                    docs_vsm[entry.doc][term] = tf*idf
                else:
                    docs_vsm[entry.doc] = {
                        term:tf*idf
                    }
                    
    # calculate dot value between each doc and the query
    # with each doc
    for d in docs_vsm:
        # start calculating
        docs_vsm[d]['dot(d,q)'] = 0
        # print(d, [docs_vsm[d][x]**2 for x in docs_vsm[d]], )
        docs_vsm[d]['length'] = math.sqrt(sum([docs_vsm[d][x]**2 for x in docs_vsm[d]]))
        # term have to be both in query and doc 
        for term in query_vsm:
            if term in docs_vsm[d] and term != 'length':
                # print(term, end=' ')
                docs_vsm[d]['dot(d,q)'] += (docs_vsm[d][term]*query_vsm[term])
        docs_vsm[d]['cosin(d,q)'] = docs_vsm[d]['dot(d,q)'] / (docs_vsm[d]['length']*query_vsm['length'])

    docs_terms = {}
    for doc_id in docs_vsm:
        terms = [term for term in docs_vsm[doc_id] if term in query]
        docs_terms[doc_id] = terms
    
    results = []
    for d in docs_vsm:
        results.append((d, docs_vsm[d]['cosin(d,q)']))
    results = sorted(results, key=lambda x: x[1], reverse=True)
    display = ""
    if len(query) > 1:
        display = n_gram(results[:35], query, docs_terms)
    return results[:35], display, query

def n_gram(results, query, docs_terms):
    """
        generate n-word phrases from query 
        then search for phrases in doc 
    """
    n_grams = []
    for i in range(2, len(query)+1):
        for j in range(len(query)):
            temp = query[j:j+i]
            if len(temp) > 1:
                n_grams.append(' '.join(temp))
    query = n_grams
    
    docs = []
    for id,_ in results:
        filter_result = Doc.objects.filter(id=id)
        docs.append((filter_result[0].id, process_doc_for_n_gram(filter_result[0].content)))
    #===================== Reranking based on phrases match =====================#
    reranking = []
    for id, doc in docs:
        reranking.append((id, set([term for term in query if term in doc] + docs_terms[id])))
    reranking = list(sorted(reranking, key=lambda x: len(x[1]), reverse=True))
    print(*reranking, sep='\n')
    #===================== Display result without reranking ==================#
    # for id, doc in docs:
        # print((id, set([term for term in query if term in doc])))
    return reranking

def process_doc_for_n_gram(doc):
    # remove speical entities 
    doc = re.sub(r'&amp;', ' ', doc)
    doc = re.sub(r'&lt; ', '', doc)
    doc = re.sub(r'\n', ' ', doc)
    doc = re.sub(r' +', ' ', doc)
    # split by space 
    tokens = doc.strip().split()
    length = 0
    result = ""
    for token in tokens:
        remove = remove_punctutations(token.strip())
        remove = remove.strip()
        #print(token,"->",remove)
        if len(token) > 1 and token not in stop_words:
            result += " " + remove
    result = re.sub(r' +', ' ', result)
    return result.strip()

# for query in search_queries:
# retrieval(search_queries[0])
