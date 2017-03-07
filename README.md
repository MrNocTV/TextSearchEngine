# TextSearchEngine
This search engine is a project for MIR (Media Information Retrieval) class
It uses:
- Django Framwork
- Python3
- Applying Vector Space Model for searching and ranking
- Reranking with "N-words" matches.

IR is the main and only (django) application. 
To start, check out the pre_processing.py, this Python file involves:
+ Pre processing (tokenization, remove punctuations and stop words)
+ Dump docs and terms to database 
+ Indexing
+ Retrieval
+ Ranking (using cosin formula)
+ Reranking (using "N-words" matches - inspired from N-gram or Edge N-gram)

The project structure follow Django's standards structure (Django >= 1.8)
