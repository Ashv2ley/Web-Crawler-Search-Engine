import zipfile
import json
import re
import shelve
import pickle

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
    tf_idf: int = 0
    ps: PorterStemmer = PorterStemmer()
    indexDict: DefaultDict[str, List] = field(default_factory = lambda: defaultdict(list))
    uniqueTokens: Set[str] = field(default_factory = set)
    searchTokens: List[str] = field(default_factory = list)


app = Flask(__name__, static_url_path='/static')
stats = indexStats()
# with shelve.open("shelf") as shelf:
#     shelf["index"] = stats.indexDict

# shelf = shelve.open("shelf")



@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=['GET'])
def search():
    query = request.args.get('query')
    global stats
    if bool(
            re.search(r'\band\b', query.lower(), flags=re.IGNORECASE)):
        tokens = query.split("and")
        stats.searchTokens = [stats.ps.stem(token) for token in tokens]
    else:
        tokens = query.split(" ")
        stats.searchTokens = [stats.ps.stem(token) for token in tokens]

    searchIndex()
    return render_template("index.html", query = query)





def valid(url, content):
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



def writeReport():
    """class that writes data to a file"""
    with open('report.txt', 'w') as file:
        file.write("Number of documents: 0\n")
        file.write("Number of [unique] tokens: 0\n")
        file.write("Total size (in KB): 0\n")

    with open("report.txt", "r") as report:
        lines = report.readlines()

    # read from each line and update any values
    for i, line in enumerate(lines):

        if "Number of documents:" in line:
            lines[i] = f"Number of documents: {stats.numDocs}\n"
        elif "Number of [unique] tokens:" in line:
            lines[i] = f"Number of [unique] tokens: {len(stats.uniqueTokens)}\n"
        elif "Total size (in KB):" in line:
            lines[i] = f"Total size (in KB): {stats.totalSize}\n"


    with open("report.txt", "w") as report:
        report.writelines(lines)


def readZip(path:str):
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
        # print(file_list)
        for file_name in file_list:
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


    #             with shelve.open("shelf") as shelf:
    #                 shelf["index"] = stats.indexDict
    # # print(stats.indexDict)
    # #make a shelve and store the inverted index then refer to the shelve when getting the tf_idf score

def merge(num:int):
    """
    merges partial indexes
    :param num:
    :return:
    """
    for i in range(num):
        with open(f"index_{i+1}.pkl", "rb") as file:
            indexData = pickle.load(file)
            stats.indexDict.update(indexData)


def create_partial_index(index):
    num_partitions = 3
    partSize = len(stats.indexDict) // num_partitions
    for i in range(num_partitions):
        start = i * partSize
        end = (i+1) * partSize

        splitData = {k: stats.indexDict[k] for k in list(stats.indexDict)[start:end]}
        with open(f'index_{i + 1}.pkl', 'wb') as file:
            pickle.dump(splitData, file)

def save_to_shelve(index):
    with shelve.open("index_shelf") as shelf:
        # Store the dictionary in the shelve
        shelf['index'] = pickle.dumps(index)

# def print_shelve():
#     with shelve.open("index_shelf") as shelf:
#         # Retrieve and print the stored dictionary
#         stored_data = shelf.get('index', {})
#         # print("Contents of the shelve:")
#         print(stored_data)

def searchIndex():
    with shelve.open("index_shelf") as shelf:
        # Retrieve and print the stored dictionary
        stored_data = shelf.get('index', {})
        unpickled_data = pickle.loads(stored_data)
        for token in stats.searchTokens:
            result = unpickled_data.get(token)
            print(result)


        # print(stored_data)


if __name__ == "__main__":
    stats = indexStats()
    if not stats.indexDict:
        merge(3)

    print("Done indexing!")
    print(len(stats.indexDict))
    print(stats.indexDict["hello"])



    # zip_file_path = "C:\\Users\\Antonio\\Downloads\\developer.zip"
    # readZip(zip_file_path)
    # create_partial_index(stats.indexDict)
    # app.run(debug = True, port = 8000)
