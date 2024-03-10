import zipfile
import json
import re
import pickle


from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup
from InvertedIndex import valid
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import pandas as pd
from scipy.sparse import save_npz, load_npz
from scipy.sparse import csr_matrix
from InvertedIndex import indexStats
from collections import Counter

def tfidfCalc(path):
    stemmer = PorterStemmer()
    urls = [
    ]
    content = []
    with zipfile.ZipFile(path, 'r') as zip_ref:
        # List all files in the zip archive
        file_list = zip_ref.namelist()
        # Iterate through each file in the zip archive
        i = 0
        for file_name in file_list:
            # Check if the file is a JSON file (you can customize this condition)
            if file_name.endswith('.json'):
                # Read the JSON content directly from the zip archive
                with zip_ref.open(file_name) as json_file:
                    # Load JSON content
                    json_data = json.load(json_file)
                    if not valid(json_data['url'], json_data['content']):
                        pass
                    soup = BeautifulSoup(json_data['content'], "html.parser")
                    alphanumeric_words = re.findall(r'\b\w+\b', soup.get_text())
                    corpus = " ".join(stemmer.stem(word.lower()) for word in alphanumeric_words)
                    urls.append(json_data['url'])
                    content.append(corpus)
                    i+=1
                    if i % 100 == 0:
                        print(i)
                    # if i == 2000:
                    #     break

    print("CREATING VECTOR")
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(content)
    # save_npz("tfidf_vectorizer.npz", vectorizer)
    try:
        df = pd.DataFrame(matrix.toarray(), index = urls, columns = vectorizer.get_feature_names_out())

        return df
    except:
        print("dataframe unavailable")

        return vectorizer


def readZip2(path: str):
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

                    i+= 1
                    if i % 100 == 0:
                        print(i)
def offload(obj):
    with open("vectorizer.pkl", 'wb') as file:
        pickle.dump(obj, file)

def load(path="vectorizer.pkl"):

    with open(path, 'rb') as file:
        return pickle.load(file)


def create_partial_index():
    num_partitions = 7
    partSize = len(stats.indexDict) // num_partitions
    for i in range(num_partitions):
        start = i * partSize
        end = (i+1) * partSize

        splitData = {k: stats.indexDict[k] for k in list(stats.indexDict)[start:end]}
        with open(f'index_w_tfidf_{i + 1}.pkl', 'wb') as file:
            pickle.dump(splitData, file)
def merge(num:int):
    """
    merges partial indexes
    :param num:
    :return:
    """
    for i in range(num):
        with open(f"index_w_tfidf_{i+1}.pkl", "rb") as file:
            indexData = pickle.load(file)
            stats.indexDict.update(indexData)



if __name__ == "__main__":
    stats = indexStats()

    readZip2("developer.zip") #Pass through the path to the zip file 
    create_partial_index()
