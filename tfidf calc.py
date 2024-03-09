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
from InvertedIndex import valid
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import pandas as pd
from scipy.sparse import save_npz, load_npz

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
    save_npz("tfidf_matrix.npz", matrix)
    try:
        df = pd.DataFrame(matrix.toarray(), index = urls, columns = vectorizer.get_feature_names_out())

        return df
    except:
        print("dataframe unavailable")

        return matrix

def offload(obj):
    with open("dataframe.pkl", 'wb') as file:
        pickle.dump(obj, file)

def load(path="dataframe.pkl"):

    with open(path, 'rb') as file:
        return pickle.load(file)

if __name__ == "__main__":
    # df = tfidfCalc("C:\\Users\\Antonio\\Downloads\\developer.zip")
    # offload(df)
    # print(load())
    # print(os.path.getsize("dataframe.pkl"))
    # print(os.path.getsize("tfidf_matrix.npz"))
    loaded = load_npz("tfidf_matrix.npz")
    # loaded2 = load()
    # print(loaded2)
    print(loaded)