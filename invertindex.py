#!/usr/bin/python

'''
Created on 22-Feb-2014

@author: mayanknarasimhan
'''

from itertools import izip
from timeit import default_timer 

DOCINDEXFILE = 'doc_index.txt'
TERMINDEXFILE = 'term_index.txt'
TERMINFOFILE = 'term_info.txt'

def main():
    start = default_timer()
    doc_index = open(DOCINDEXFILE, 'rU')
    stop = 0
    termIndex = {}
    
    for line in doc_index.readlines():
        invIndex = {}
        stop += 1
        pieces = line.strip().split('\t')
        docid = int(pieces[0])
        termid = int(pieces[1])
        positions = [int(x) for x in pieces[2:]]
        
        if termid not in termIndex:
            delta_docid = docid - getPrevious(invIndex)
            delta_positions = ['%d:%d' %(delta_docid, positions[0])]
            delta_positions.extend(['%d:%d' %(0, y-x) for x, y in izip(positions[:-1], positions[1:])])
            invIndex[docid] = delta_positions
            termIndex[termid] = invIndex
        else:
            invIndex = termIndex[termid]
            delta_docid = docid - getPrevious(invIndex)
            delta_positions = ['%d:%d' %(delta_docid, positions[0])]
            delta_positions.extend(['%d:%d' %(0, y-x) for x, y in izip(positions[:-1], positions[1:])])
            invIndex[docid] = delta_positions
            termIndex[termid] = invIndex
            
#         if stop == 200:
#             break
    doc_index.close()
    writeFiles(termIndex)
    print 'Completed in: %f seconds' %(default_timer() - start)
    
        
def getPrevious(odict):
    previous = 0
    if odict:
        previous = sorted(odict.keys())[-1]
    return previous

def writeFiles(termIndex):
    term_index = open(TERMINDEXFILE, 'w')
    term_info = open(TERMINFOFILE, 'w')
    seekOffset = 0
    for termid in termIndex:
        docPostns = '%d\t%s\n' %(termid, '\t'.join(['\t'.join(termIndex[termid][key]) for key in sorted(termIndex[termid].iterkeys())]))
        termFrequency = sum(len(values) for values in termIndex[termid].itervalues())
        docFrequency = len(termIndex[termid])
        termInfo = '%d\t%d\t%d\t%d\n' %(termid, seekOffset, termFrequency, docFrequency)
        term_index.write(docPostns)
        term_info.write(termInfo)
        seekOffset = term_index.tell()
    #doc_postns = '\n'.join('%d\t%s' %(termid, '\t'.join('\t'.join(values) for values in termIndex[termid].itervalues())) for termid in termIndex.iterkeys())
    #term_index.write(doc_postns)
    term_info.close()
    term_index.close()


if __name__ == '__main__':
    main()