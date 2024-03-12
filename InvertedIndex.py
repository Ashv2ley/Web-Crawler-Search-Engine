import sys
import zipfile
import json
import re
import shelve
import pickle
import threading
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from urllib.parse import urlparse
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup
from dataclasses import dataclass,field
from collections import Counter, defaultdict
from typing import DefaultDict, List, Set
from flask import Flask, render_template, request
import os.path

@dataclass
class indexStats():
    """
    Class that keeps track of all the stats of the index
    """
    numDocs: int = 0
    length: int=0
    uniquePages: int = 0
    totalSize: int = 0
    hits: int = 0
    tf: int = 0
    ifd: int = 0
    tf_idf: int = 0
    ps: PorterStemmer = PorterStemmer()
    indexDict: DefaultDict[str, List] = field(default_factory = lambda: defaultdict(list))
    tf_idf_values: DefaultDict[str, List] = field(default_factory = lambda: defaultdict(list))
    uniqueTokens: Set[str] = field(default_factory = set)
    searchTokens: List[str] = field(default_factory = list)
    top_urls: List[str] = field(default_factory = list)


app = Flask(__name__, static_url_path='/static')
stats = indexStats()




@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=['GET'])
def search():
    query = request.args.get('query')

    # global stats
    if bool(
            re.search(r'\band\b', query.lower(), flags=re.IGNORECASE)):
        tokens = query.split("and")
        stats.searchTokens = [stats.ps.stem(token) for token in tokens]
    else:
        tokens = query.split(" ")
        stats.searchTokens = [stats.ps.stem(token) for token in tokens]

    searchIndex()
    return render_template("index.html", urls = stats.top_urls, search=query, hits=stats.hits)



def valid(url, content):
    """checks if url is a valid html file"""
    parsed = urlparse(url)
    if not parsed.path.endswith(".html"):
        return False
    try:
        soup = BeautifulSoup(content, "html.parser")
    except:
        return False

    if "html" not in soup.contents[0]:
        return False
    return True



# def writeReport():
#     """class that writes data to a file"""
#     with open('report.txt', 'w') as file:
#         file.write("Number of documents: 0\n")
#         file.write("Number of [unique] tokens: 0\n")
#         file.write("Total size (in KB): 0\n")
# 
#     with open("report.txt", "r") as report:
#         lines = report.readlines()
# 
#     # read from each line and update any values
#     for i, line in enumerate(lines):
# 
#         if "Number of documents:" in line:
#             lines[i] = f"Number of documents: {stats.numDocs}\n"
#         elif "Number of [unique] tokens:" in line:
#             lines[i] = f"Number of [unique] tokens: {len(stats.uniqueTokens)}\n"
#         elif "Total size (in KB):" in line:
#             lines[i] = f"Total size (in KB): {stats.totalSize}\n"
# 
# 
#     with open("report.txt", "w") as report:
#         report.writelines(lines)


def index(path:str):
    """
    Takes in a path to a zip file, and reads its contents
    :param path:
        path to the zip file
    :return: None
    """

    # Open the zip file
    with zipfile.ZipFile(path, 'r') as zip_ref:
        # List all files in the zip archive
        file_list = zip_ref.namelist()
        # Iterate through each file in the zip archive
        for file_name in file_list:
            stats.numDocs+=1
            # Check if the file is a JSON file (you can customize this condition)
            if file_name.endswith('.json'):
                # Read the JSON content directly from the zip archive
                with zip_ref.open(file_name) as json_file:
                    # Load JSON content
                    json_data = json.load(json_file)
                    if not valid(json_data['url'], json_data['content']):
                        pass
                    stats.numDocs += 1
                    soup = BeautifulSoup(json_data['content'], "html.parser")
                    alphanumeric_words = re.findall(r'\b\w+\b', soup.get_text())
                    corpus = [stats.ps.stem(word.lower()) for word in alphanumeric_words] #all words in a file
                    num_of_words_in_file = len(corpus)
                    counter = Counter(corpus)
                    #gets each word and frequency in each file
                    for word, count in counter.items():

                        stats.indexDict[word].append((json_data['url'], count))


def merge(num:int):
    """
    merges partial indexes
    :param num:
    :return:
    """
    for i in range(num):
        with open(f"partial indexes/index_{i+1}.pkl", "rb") as file:
            indexData = pickle.load(file)
            stats.indexDict.update(indexData)

def mergeTifidf(num:int):
    for i in range(num):
        with open(f"index_w_tfidf_{i+1}.pkl", "rb") as file:
            indexData = pickle.load(file)
            stats.tf_idf_values.update(indexData)


def create_partial_index():
    num_partitions = 3
    partSize = len(stats.indexDict) // num_partitions
    for i in range(num_partitions):
        start = i * partSize
        end = (i+1) * partSize

        splitData = {k: stats.indexDict[k] for k in list(stats.indexDict)[start:end]}
        with open(f'index_w_tfidf_{i + 1}.pkl', 'wb') as file:
            pickle.dump(splitData, file)

# def save_to_shelve(index):
#     """saves index to disk"""
#     with shelve.open("index_shelf") as shelf:
#         # Store the dictionary in the shelve
#         shelf['index'] = pickle.dumps(index)

def calculateTFIDF(path: str):
    """
    Takes in a path to a zip file, and reads its contents
    :param path:
        path to the zip file
    :return: None
    """

    # Initialize TfidfVectorizer
    vectorizer = TfidfVectorizer()

    # Open the zip file
    with zipfile.ZipFile(path, 'r') as zip_ref:
        # List all files in the zip archive
        file_list = zip_ref.namelist()

        # Iterate through each file in the zip archive
        i = 0
        for file_name in file_list:
            stats.numDocs += 1

            # Check if the file is a JSON file (you can customize this condition)
            if file_name.endswith('.json'):
                # Read the JSON content directly from the zip archive
                with zip_ref.open(file_name) as json_file:
                    # Load JSON content
                    json_data = json.load(json_file)

                    if not valid(json_data['url'], json_data['content']):
                        pass

                    stats.numDocs += 1
                    soup = BeautifulSoup(json_data['content'], "html.parser")

                    alphanumeric_words = re.findall(r'\b\w+\b', soup.get_text())
                    corpus = [stats.ps.stem(word.lower()) for word in
                              alphanumeric_words]  # all words in a file

                    # Convert the list of words into a string for TfidfVectorizer
                    document_text = ' '.join(corpus)

                    # Vectorize the document using TF-IDF
                    try:
                        tfidf_matrix = vectorizer.fit_transform([document_text])
                    except ValueError:
                        pass
                    feature_names = vectorizer.get_feature_names_out()

                    # Get each word and its TF-IDF score in the document
                    for word, tfidf_score in zip(feature_names, tfidf_matrix.toarray()[0]):
                        # only increment if a heading or bold
                        if word.lower() in [heading.text.lower() for heading in soup.find_all(['h1', 'h2', 'h3'])]:
                            tfidf_score += 2

                        if word.lower() in [word for bold_tag in soup.find_all('b') for word in re.findall(r'\b\w+\b', bold_tag.get_text())]:
                            tfidf_score += 1.5

                    if i % 100 == 0:
                        print(i)
                    i += 1


def create_partial_index():
    num_partitions = 3
    partSize = len(stats.indexDict) // num_partitions
    for i in range(num_partitions):
        start = i * partSize
        end = (i+1) * partSize

        splitData = {k: stats.indexDict[k] for k in list(stats.indexDict)[start:end]}
        with open(f'index_w_tfidf_{i + 1}.pkl', 'wb') as file:
            pickle.dump(splitData, file)
def searchIndex():
    matching_urls = None
    for token in stats.searchTokens:
        result = stats.indexDict.get(token)

        # Update matching_urls based on the current token
        if result:
            if matching_urls is None:
                matching_urls = set(result)
            else:
                matching_urls.intersection_update(result)

            # store top 5 urls tht contain all tokens
        if matching_urls:
            sorted_data = sorted(matching_urls, key=lambda x: x[1], reverse=True)
            stats.top_urls = sorted_data[:5]
            stats.hits = len(sorted_data)
        else:
            stats.top_urls = ["No matching URLs found."]


if __name__ == "__main__":
    command = input('Type "index" to create index or type "run" to run application:\n')
    if command == "index":
        path = input("Enter the path to zip file:\n").strip('"')
        calculateTFIDF(path)
        create_partial_index()
    if command == "run":

        stats = indexStats()

        if not stats.tf_idf_values:
            print("Indexing...")
            with open("index_w_tfidf_1.pkl", 'rb') as file:
                # content = pickle.load(file)
                # print(content)
            mergeTifidf(3)

            # Wait for both threads to finish

            print("Index Complete!")

    # zip_file_path = 'developer.zip'
    # index(zip_file_path)
    # save_to_shelve(stats.indexDict)
        app.run(debug = True, port = 8000)
