#!/usr/bin/python

'''
Created on 19-Mar-2014

@author: mayanknarasimhan
'''

from timeit import default_timer
from argparse import ArgumentParser
from lxml import etree
from math import sqrt, log10
from random import randint
import re
import read_index

TOPICSXMLFILE = 'topics.xml'


def main():
    start = default_timer()

    parser = ArgumentParser()
    parser.add_argument('--score', help='the scoring function to be used')
    args = parser.parse_args()

    scoring_functions = {'TF': score_tf,
                         'TF-IDF': score_tfidf,
                         'BM25': score_bm25,
                         'Laplace': score_laplace,
                         'JM': score_jm}

    if args.score:
        queries = getQueries()
        doc_stats = read_index.getDocTermFreqs()
        all_docs = read_index.getAllDocs()
        all_docs_length = len(all_docs)
        avgDocLength = 0
        for docId in doc_stats:
            avgDocLength = avgDocLength + len(doc_stats[docId])
        avgDocLength = avgDocLength / all_docs_length

        score_function = scoring_functions[args.score.strip()]
        if score_function:
            score_function(doc_stats, avgDocLength, queries, all_docs)

            #print 'Completed in: %f seconds' % (default_timer() - start)


def getQueries():
    xmlParser = etree.XMLParser()
    doc = etree.parse(TOPICSXMLFILE, parser=xmlParser)
    queries = {}
    for element in doc.xpath('//topic'):
        queryNum = int(element.attrib['number'])
        #queryText = element[0].text.strip().split()
        queryText = element[0].text.strip()
        queryText = re.split(r'\W+(\.?\W+)*', queryText, flags=re.IGNORECASE)
        queries[queryNum] = queryText

    return queries


def oktf(obj, termId, doc_stats, avgDocLength, argType, docLength=0, query_stats=None):
    if argType == 'doc':
        docId = obj
        tf = doc_stats[docId][termId]
        oktf_doc = tf / (tf + 0.5 + (1.5 * (docLength / avgDocLength)))
        return oktf_doc
    else:
        queryList = obj
        oktf_query = 0
        tf = query_stats[termId]
        #print tf, len(queryList), avgDocLength
        oktf_query = tf / (tf + 0.5 + (1.5 * (len(queryList) / avgDocLength)))
        return oktf_query


def get_query_frequencies(query_list, vocab):
    query_stats = {}
    for query in query_list:
        if query in vocab:
            termId = vocab[query]
            if query not in query_stats:
                query_stats[termId] = 1
            else:
                query_stats[termId] += 1
    return query_stats


def score_tf(doc_stats, avgDocLength, queries, all_docs):
    vocab = read_index.getVocab()
    avg_query_length = 0
    for query_num in queries:
        avg_query_length += len(queries[query_num])
    all_queries_length = len(queries)
    avg_query_length /= all_queries_length

    for queryNum in sorted(queries):
        queryList = read_index.processQueries(queries[queryNum])
        queryVector = {}
        queryNorm = 0
        query_stats = get_query_frequencies(queryList, vocab)

        for query in queryList:
            if query in vocab:
                termId = vocab[query]
                queryVector[termId] = oktf(queryList, termId, doc_stats, avg_query_length, 'query', 0, query_stats)
                queryNorm = queryNorm + (queryVector[termId] * queryVector[termId])
        queryPair = (queryVector, queryNorm)

        doc_scores = {}
        for docId in sorted(doc_stats):
            docLength = sum(doc_stats[docId].itervalues())
            score = calculate_tf_score(docId, queryPair, doc_stats, avgDocLength, docLength)
            doc_scores[docId] = score

        for rank, docId in enumerate(sorted(doc_scores, key=doc_scores.get, reverse=True), start=1):
            print '%d 0 %s %d %f run1' % (queryNum, all_docs[docId], rank, doc_scores[docId])


def calculate_tf_score(docId, queryPair, doc_stats, avgDocLength, docLength):
    queryVector = queryPair[0]
    queryNorm = queryPair[1]
    docVector = {}
    dotProd = 0
    docNorm = 0
    for termId in doc_stats[docId]:
        docVector[termId] = oktf(docId, termId, doc_stats, avgDocLength, 'doc', docLength, None)
        docNorm += (docVector[termId] * docVector[termId])
        if termId in queryVector:
            dotProd += (docVector[termId] * queryVector[termId])

    score = dotProd / sqrt(docNorm * queryNorm)
    return score


def calculate_tfidf_score(docId, queryPair, doc_stats, avgDocLength, docLength, all_docs_length, vocab_occurrences):
    queryVector = queryPair[0]
    queryNorm = queryPair[1]
    docVector = {}
    dotProd = 0
    docNorm = 0
    for termId in doc_stats[docId]:
        oktf_i = oktf(docId, termId, doc_stats, avgDocLength, 'doc', docLength, None)
        df_i = vocab_occurrences[termId]
        docVector[termId] = oktf_i * log10(all_docs_length / df_i)
        docNorm += (docVector[termId] * docVector[termId])
        if termId in queryVector:
            dotProd += (docVector[termId] * queryVector[termId])

    score = dotProd / sqrt(docNorm * queryNorm)
    return score


def score_tfidf(doc_stats, avgDocLength, queries, all_docs):
    vocab = read_index.getVocab()
    query_occurrences = get_query_occurrences(queries, vocab)
    vocab_occurrences = read_index.getTermOccuurences()

    avg_query_length = 0
    for query_num in queries:
        avg_query_length += len(queries[query_num])
    all_queries_length = len(queries)
    avg_query_length /= all_queries_length

    for queryNum in sorted(queries):
        queryList = read_index.processQueries(queries[queryNum])
        queryVector = {}
        queryNorm = 0
        query_stats = get_query_frequencies(queryList, vocab)

        for query in queryList:
            if query in vocab:
                termId = vocab[query]
                oktf_i = oktf(queryList, termId, doc_stats, avg_query_length, 'query', 0, query_stats)
                df_i = query_occurrences[termId]
                queryVector[termId] = oktf_i * log10(all_queries_length / df_i)
                queryNorm = queryNorm + (queryVector[termId] * queryVector[termId])
        queryPair = (queryVector, queryNorm)

        doc_scores = {}
        for docId in sorted(doc_stats):
            docLength = sum(doc_stats[docId].itervalues())
            score = calculate_tfidf_score(docId, queryPair, doc_stats, avgDocLength, docLength, len(all_docs),
                                          vocab_occurrences)
            doc_scores[docId] = score

        for rank, docId in enumerate(sorted(doc_scores, key=doc_scores.get, reverse=True), start=1):
            print '%d 0 %s %d %f run1' % (queryNum, all_docs[docId], rank, doc_scores[docId])


def get_query_occurrences(queries, vocab):
    query_occurrences = {}
    query_list = []
    for query_num in queries:
        query_list.extend(read_index.processQueries(queries[query_num]))

    for query_term in query_list:
        if query_term in vocab:
            term_id = vocab[query_term]
            if term_id not in query_occurrences:
                query_occurrences[term_id] = 1
            else:
                query_occurrences[term_id] += 1
    return query_occurrences


def score_bm25(doc_stats, avgDocLength, queries, all_docs):
    vocab = read_index.getVocab()
    vocab_occurrences = read_index.getTermOccuurences()
    k1 = 1.2
    k2 = 100  #randint(0, 1000)
    b = 0.75
    all_docs_length = len(all_docs)

    for query_num in sorted(queries):
        query_list = read_index.processQueries(queries[query_num])
        query_stats = get_query_frequencies(query_list, vocab)
        doc_scores = {}
        for doc_id in sorted(doc_stats):
            score = 0
            for query_term in query_list:
                if query_term in vocab:
                    term_id = vocab[query_term]
                    tf_qi = query_stats[term_id]

                    if term_id in doc_stats[doc_id]:
                        df_i = vocab_occurrences[term_id]
                        operand1 = log10((all_docs_length + 0.5) / (df_i + 0.5))

                        tf_di = doc_stats[doc_id][term_id]
                        doc_length = sum(doc_stats[doc_id].itervalues())
                        K = k1 * ((1 - b) + b * (doc_length / avgDocLength))
                        operand2 = (1 + k1) * tf_di / (K + tf_di)

                        operand3 = (1 + k2) * tf_qi / (k2 + tf_qi)

                        score += operand1 * operand2 * operand3
                        doc_scores[doc_id] = score

        for rank, docId in enumerate(sorted(doc_scores, key=doc_scores.get, reverse=True), start=1):
            print '%d 0 %s %d %f run1' % (query_num, all_docs[docId], rank, doc_scores[docId])


def score_laplace(doc_stats, avgDocLength, queries, all_docs):
    vocab = read_index.getVocab()

    for query_num in sorted(queries):
        query_list = read_index.processQueries(queries[query_num])
        doc_scores = {}
        for doc_id in sorted(doc_stats):
            score = 0
            for query_term in query_list:
                if query_term in vocab:
                    term_id = vocab[query_term]
                    tf_di = 0
                    if term_id in doc_stats[doc_id]:
                        tf_di = doc_stats[doc_id][term_id]
                    doc_length = sum(doc_stats[doc_id].itervalues())
                    probability_di = (tf_di + 1) / (doc_length + float(len(vocab)))
                    score += log10(probability_di)
                    doc_scores[doc_id] = score

        for rank, docId in enumerate(sorted(doc_scores, key=doc_scores.get, reverse=True), start=1):
            print '%d 0 %s %d %f run1' % (query_num, all_docs[docId], rank, doc_scores[docId])


def score_jm(doc_stats, avgDocLength, queries, all_docs):
    vocab = read_index.getVocab()
    term_freq = read_index.get_term_frequencies()
    corpus_length = 0
    for doc_id in doc_stats:
        corpus_length += sum(doc_stats[doc_id].itervalues())

    lamda = 0.99

    for query_num in sorted(queries):
        query_list = read_index.processQueries(queries[query_num])
        doc_scores = {}
        for doc_id in sorted(doc_stats):
            score = 0
            for query_term in query_list:
                if query_term in vocab:
                    term_id = vocab[query_term]
                    operand1 = 0
                    if term_id in doc_stats[doc_id]:
                        tf_di = doc_stats[doc_id][term_id]
                        doc_length = sum(doc_stats[doc_id].itervalues())
                        operand1 = tf_di / (float(doc_length))

                    operand2 = term_freq[term_id] / float(corpus_length)
                    probability_di = ((1 - lamda) * operand1) + (lamda * operand2)
                    score += log10(probability_di)
                    doc_scores[doc_id] = score

        for rank, docId in enumerate(sorted(doc_scores, key=doc_scores.get, reverse=True), start=1):
            print '%d 0 %s %d %f run1' % (query_num, all_docs[docId], rank, doc_scores[docId])


if __name__ == '__main__':
    main()