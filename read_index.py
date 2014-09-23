#!/usr/bin/python

'''
Created on 22-Feb-2014

@author: mayanknarasimhan
'''

from timeit import default_timer 
from argparse import ArgumentParser
from Stemmer import Stemmer
import tokenize

DOCINDEXFILE = 'doc_index.txt'
TERMINDEXFILE = 'term_index.txt'
TERMINFOFILE = 'term_info.txt'
DOCIDSFILE = 'docids.txt'
TERMIDSFILE = 'termids.txt'

def main():
    start = default_timer()
    parser = ArgumentParser()
    parser.add_argument('--doc', help='the document to lookup information')
    parser.add_argument('--term', help='the term to lookup information')
    args = parser.parse_args()
    
    if args.term and args.doc:
        term_ids = getTerm(args.term.strip())
        if term_ids:
            term_stats = getTermStats(term_ids[term_ids.keys()[0]])
            doc_ids = getDoc(args.doc.strip())
            if doc_ids:
                doc_stats = getDocStats(doc_ids[doc_ids.keys()[0]])
                term = args.term.strip()
                termId = term_ids[term_ids.keys()[0]]
                docName = args.doc.strip()
                docId = doc_ids[docName]
                distinctTerms = doc_stats[docId][0]
                totalTerms = doc_stats[docId][1]
                invertedListOffset = term_stats[termId][0]
        
                term_index_file = open(TERMINDEXFILE, 'rU')
                term_index_file.seek(invertedListOffset)
                line = term_index_file.readline()
                term_index_file.close()
                pieces = line.strip().split('\t')
                invertedList = pieces[1:]
                invertedTable = {}
                prevDocId = 0
                prevPostn = 0
                
                for item in invertedList:
                    postns = []
                    invertedDocId = int(item.split(':')[0]) + prevDocId
                    postnOffset = int(item.split(':')[1])
                    if invertedDocId == docId:
                        if invertedDocId not in invertedTable:
                            prevPostn = 0
                            postns.append(postnOffset + prevPostn)
                            invertedTable[invertedDocId] = postns
                            prevPostn += postnOffset
                        else:
                            postns = invertedTable[invertedDocId]
                            postns.append(postnOffset + prevPostn)
                            invertedTable[invertedDocId] = postns
                            prevPostn += postnOffset
                    prevDocId = invertedDocId
                    
                if invertedTable:
                    print 'Inverted list for: %s' %(term)
                    print 'In document: %s' %(docName)
                    print 'TERMID: %d' %(termId)
                    print 'DOCID: %d' %(docId)
                    print 'Term frequency in document: %d' %(len(invertedTable[docId]))
                    print 'Positions: %s' %(', '.join([str(x) for x in invertedTable[docId]]))
                else:
                    print 'Term %s not present in document: %s' %(term, docName)
                
            else:
                print 'Document does not exist in the corpus'
        else:
            print 'Term does not exist in the corpus'
        
    elif args.term:
        term_ids = getTerm(args.term.strip())
        if term_ids:
            term_stats = getTermStats(term_ids[term_ids.keys()[0]])
            term = args.term.strip()
            termId = term_ids[term_ids.keys()[0]]
            print 'Listing for term: %s' %(term)
            print 'TERMID: %d' %(termId)
            print 'Number of documents containing term: %d' %(term_stats[termId][2])
            print 'Term frequency in corpus: %d' %(term_stats[termId][1])
            print 'Inverted list offset: %d' %(term_stats[termId][0])
        else:
            print 'Term does not exist in the corpus'
        
    elif args.doc:
        doc_ids = getDoc(args.doc.strip())
        if doc_ids:
            doc_stats = getDocStats(doc_ids[doc_ids.keys()[0]])
            docName = args.doc
            docId = doc_ids[docName]
            distinctTerms = doc_stats[docId][0]
            totalTerms = doc_stats[docId][1]
            print 'Listing for document: %s' %(docName)
            print 'DOCID: %d' %(docId)
            print 'Distinct Terms: %d' %(distinctTerms)
            print 'Total Terms: %d' %(totalTerms)
        else:
            print 'Document does not exist in the corpus'
        
    print 'Completed in: %f seconds' %(default_timer() - start)
    
def getDocStats(docId):
    doc_stats = {}
    doc_index_file = open(DOCINDEXFILE, 'rU')
    
    for line in doc_index_file.readlines():
        pieces = line.strip().split('\t')
        doc_id = int(pieces[0])
        if docId == doc_id:
            termFreq = len(pieces[2:])
            if docId not in doc_stats:
                termCount = []
                termCount.append(1)
                termCount.append(termFreq) 
                doc_stats[docId] = termCount
            else:
                termCount = doc_stats[docId]
                termCount[0] += 1
                termCount[1] += termFreq
                doc_stats[docId] = termCount
        if doc_id > docId:
            return doc_stats
    
    doc_index_file.close()
    return doc_stats

def getDocTermFreqs():
    doc_stats = {}
    doc_index_file = open(DOCINDEXFILE, 'rU')
    
    for line in doc_index_file.readlines():
        pieces = line.strip().split('\t')
        doc_id = int(pieces[0])
        termFreq = len(pieces[2:])
        termId = int(pieces[1])
        if doc_id not in doc_stats:
            term_info = {}
            term_info[termId] = termFreq
            doc_stats[doc_id] = term_info
        else:
            term_info = doc_stats[doc_id]
            term_info[termId] = termFreq
            doc_stats[doc_id] = term_info
    
    doc_index_file.close()
    return doc_stats

def getTermStats(termId):
    term_stats = {}
    term_info_file = open(TERMINFOFILE, 'rU')
    
    for line in term_info_file.readlines():
        pieces = line.strip().split('\t')
        term_id = int(pieces[0])
        if termId == term_id:
            seekOffset = int(pieces[1])
            termFreq = int(pieces[2])
            docFreq = int(pieces[3])
            term_stats[termId] = (seekOffset, termFreq, docFreq)
            return term_stats
        
    term_info_file.close()
    return term_stats


def get_term_frequencies():
    term_stats = {}
    term_info_file = open(TERMINFOFILE, 'rU')

    for line in term_info_file.readlines():
        pieces = line.strip().split('\t')
        term_id = int(pieces[0])
        term_freq = int(pieces[2])
        term_stats[term_id] = term_freq

    term_info_file.close()
    return term_stats

def getTermOccuurences():
    term_stats = {}
    term_info_file = open(TERMINFOFILE, 'rU')
    
    for line in term_info_file.readlines():
        pieces = line.strip().split('\t')
        term_id = int(pieces[0])
        if term_id not in term_stats:
            docFreq = int(pieces[3])
            term_stats[term_id] = docFreq
            
    term_info_file.close()
    return term_stats

def getTerm(term):
    term_ids = {}
    term_ids_file = open(TERMIDSFILE, 'rU')
    
    for line in term_ids_file.readlines():
        pieces = line.strip().split('\t')
        stemmer = Stemmer('english')
        #stemmer.maxCacheSize = 1
        termStem = stemmer.stemWord(term.lower())
        if termStem == pieces[1]:
            term_ids[pieces[1]] = int(pieces[0])
            return term_ids
    
    term_ids_file.close()
    return term_ids

def getTermId(term):
    termId = -1
    term_ids_file = open(TERMIDSFILE, 'rU')
    
    for line in term_ids_file.readlines():
        pieces = line.strip().split('\t')
        if term == pieces[1]:
            termId = int(pieces[0])
            term_ids_file.close()
            return termId
    
    term_ids_file.close()
    return termId

def getVocab():
    vocab = {}
    term_ids_file = open(TERMIDSFILE, 'rU')
    
    for line in term_ids_file.readlines():
        pieces = line.strip().split('\t')
        vocab[pieces[1]] = int(pieces[0])
    
    term_ids_file.close()
    return vocab

def getDoc(docName):
    doc_ids = {}
    doc_ids_file = open(DOCIDSFILE, 'rU')

    for line in doc_ids_file.readlines():
        pieces = line.strip().split('\t')
        if docName == pieces[1]:
            doc_ids[pieces[1]] = int(pieces[0])
            return doc_ids
    
    doc_ids_file.close()
    return doc_ids

def getDocId(docName):
    docId = -1
    doc_ids_file = open(DOCIDSFILE, 'rU')

    for line in doc_ids_file.readlines():
        pieces = line.strip().split('\t')
        if docName == pieces[1]:
            docId = pieces[0]
            return docId
    
    doc_ids_file.close()
    return docId

def getAllDocs():
    all_docs = {}
    doc_ids_file = open(DOCIDSFILE, 'rU')

    for line in doc_ids_file.readlines():
        pieces = line.strip().split('\t')
        all_docs[int(pieces[0])] = pieces[1]
    
    doc_ids_file.close()
    return all_docs
    

def processQueries(queries):
    queryList = []
    for query in queries:
        filteredQuery = tokenize.filterToken(query, tokenize.getStopWords())
        if filteredQuery and filteredQuery is not None:
            stemmer = Stemmer('english')
            queryStem = stemmer.stemWord(filteredQuery.lower())
            queryList.append(queryStem)
    
    return queryList
    

if __name__ == '__main__':
    main()