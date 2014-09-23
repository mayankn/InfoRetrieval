InfoRetrieval
=============

Information Retrieval project

How to run:
=============

1. A tokenizer, which reads a document collection and creates documents containing indexable tokens

  ./tokenize.py --dir <directory path containing the document collection>

2. An indexer, which reads a collection of tokenized documents and constructs an inverted index 

  ./invertindex.py

3. A tool which reads the index and prints information read from it

  ./read_index.py --doc <document name to lookup>
  ./read_index.py --term <term to lookup>
  ./read_index.py --term <term to lookup> --doc <document to lookup term in>

4. A program which takes the name of a scoring function as a command line argument 
and which prints to STDOUT a ranked list of documents for all queries found in topics.xml using that scoring function

  ./query.py --score <name of scoring function>
