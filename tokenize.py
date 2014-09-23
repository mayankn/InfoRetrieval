#!/usr/bin/python


'''

@author: mayanknarasimhan
'''

from argparse import ArgumentParser
from os import listdir, path
import re
from timeit import default_timer
from BeautifulSoup import UnicodeDammit # pip install BeautifulSoup
#from stemming.porter import stem   # pip install stemming
from Stemmer import Stemmer # pip install pystemmer
from operator import itemgetter


try:
    import lxml.html.clean  # pip install lxml
except ImportError:
    None

STOPWORDSFILE = 'stoplist.txt'
DOCIDSFILE = 'docids.txt'
TERMIDSFILE = 'termids.txt'
DOCINDEXFILE = 'doc_index.txt'
terms = {}
termDict = {}

def main():
    start = default_timer()
    parser = ArgumentParser()
    parser.add_argument('-d', '--dir', help='the directory containing the document collection')
    args = parser.parse_args()
    stopWords = getStopWords()
    doc_ids = []
    doc_index = []

    for docid, fileName in enumerate(listdir(args.dir), start = 1):
        terms.clear()
        
        htmlFile = open(path.join(args.dir, fileName), 'rU')
        htmlData = htmlFile.read()
        #print 'Processing %s %s' %(docid, fileName)
        text = getText(htmlData)
        cleanedText = " ".join(text.split())
                
        getStems(cleanedText, stopWords)
        
        for termid, posList in sorted(terms.iteritems()):
            postns = '\t'.join([str(x) for x in sorted(posList)])
            doc_index_string =  '%d\t%d\t%s'  %(docid, termid, postns)
            doc_index.append(doc_index_string)
            
        doc_ids.append('%d\t%s' %(docid, fileName))  
        
        htmlFile.close()
        
    term_ids = '\n'.join(['%d\t%s' %(termid, term) for term, termid in sorted(termDict.iteritems(), key=itemgetter(1))])
    writeToFiles('\n'.join(doc_ids), term_ids, '\n'.join(doc_index))
        
    print 'Total time taken = %f seconds' % (default_timer() - start)
    
def writeToFiles(doc_ids, term_ids, doc_index):
    docIdFile = open(DOCIDSFILE, 'w')
    termIdFile = open(TERMIDSFILE, 'w')
    docIndexFile = open(DOCINDEXFILE, 'w') 
    
    docIdFile.write(doc_ids)
    termIdFile.write(term_ids)
    docIndexFile.write(doc_index)
    
    termIdFile.close()
    docIndexFile.close()
    docIdFile.close()
            
def getText(html):
    html = re.sub(r'<.*?html', '<html', html, count=1, flags=re.IGNORECASE)
    pmatch = re.search(r'<html.*?>', html, flags=re.IGNORECASE)
    begin = -1
    if pmatch is not None:
        begin = pmatch.start()
    htmlContent = ''
    if begin > -1:
        htmlContent = html[begin:]
    text = ''
    #htmlContent = html
    if htmlContent and htmlContent is not None and htmlContent != '':
        
        doc = decode_data(htmlContent)
        try:
            lxmlparser = lxml.html.HTMLParser(encoding=doc.originalEncoding)
            tree = lxml.html.document_fromstring(htmlContent, parser=lxmlparser)
            cleaner = lxml.html.clean.Cleaner(style=True)
            tree = cleaner.clean_html(tree)
            text = tree.text_content()
        except:
            tree = lxml.html.document_fromstring(doc.unicode)
            cleaner = lxml.html.clean.Cleaner(style=True)
            tree = cleaner.clean_html(tree)
            text = tree.text_content()
    
    return text

def decode_data(data):
    return UnicodeDammit(data, isHTML=True)

def filterToken(token, stopWords):
    if token and token is not None and token not in stopWords:
        return token.lower() 

def getStopWords():
    stopFile = open(STOPWORDSFILE, 'rU')
    stopWords = stopFile.read().split()
    return set(stopWords)

def getStems(cleanedText, stopWords):
    stems = {}
    matches = re.finditer(r'\w+(\.?\w+)*', cleanedText.strip(), flags=re.IGNORECASE)
    stemmer = Stemmer('english')
    #maxlength = sum(1 for _ in matches1)
    #stemmer.maxCacheSize = maxlength
    offset = len(termDict)
    tokenid = offset + 1
    position = 0
    for match in matches:
        #position = match.start()
        position += 1 
        token = match.group()
        filteredToken = filterToken(token, stopWords)
        if filteredToken and filteredToken is not None:
            wordStem = stemmer.stemWord(filteredToken.lower())
            #present = wordStem in stems
            if wordStem not in stems:
                #tokenid += 1
                stems[wordStem] = tokenid
                positions = set()
                positions.add(position)
                if wordStem not in termDict:
                    termDict[wordStem] = tokenid
                    terms[tokenid] = positions
                    tokenid = tokenid + 1
                else:
                    stemid = termDict[wordStem] 
                    terms[stemid] = positions
            else:
                stemid = termDict[wordStem]
                postns = terms[stemid]
                postns.add(position)
                terms[stemid] = postns

if __name__ == '__main__':
    main()
