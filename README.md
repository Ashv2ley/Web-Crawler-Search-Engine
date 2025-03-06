Web Crawler & Search Engine
-------------------------
As part of coursework at UCI, We undertook a comprehensive project to develop a web crawler and a search engine. This project was divided into two main parts: building a web crawler to collect data from specified UCI domains and implementing a search engine to index and retrieve relevant information from the collected data.

Objective: Implement a web crawler to gather data from specified UCI domains:

*.ics.uci.edu/*
*.cs.uci.edu/*
*.informatics.uci.edu/*
*.stat.uci.edu/*

Key Tasks:
Crawler Implementation: Installed necessary libraries and configured the crawler. Implemented a scraper function to parse web responses, extract information, and return valid URLs.
Crawler Behavior: Ensured politeness by honoring delays, avoided web traps, and handled redirects and dead URLs. Transformed relative URLs to absolute URLs.
Monitoring and Maintenance: Monitored the crawler to ensure proper functionality, addressed issues, and restarted as needed.

Analytical Deliverables:
Unique Pages: Counted unique pages by URL, ignoring fragments.
Longest Page: Identified the longest page by the number of words (excluding HTML).
Common Words: Listed the 50 most frequent words, excluding stop words.
Subdomains: Counted and listed subdomains in ics.uci.edu.
Tools and Technologies:

Libraries: BeautifulSoup, nltk, pandas, urllib.parse, collections, numpy, langchain, configparser

HOW TO USE
-------------------------
1. To begin running, first install all dependencies indicated in the requirements.txt file.
2. Next, run InvertedIndex.py
3. To create the index, type, "index" in the terminal
4. To open the search engine, type, "run"
