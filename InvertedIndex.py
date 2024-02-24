from nltk.stem import PorterStemmer
from dataclasses import dataclass
from bs4 import BeautifulSoup
import os
import zipfile
import sys
import json
import re

@dataclass
class indexStats():
    """
    Class that keeps track of all the stats of the index
    """
    numDocs: int = 0
    uniquePages: int = 0
    totalSize: int = 0


def readZip(path:str):
    """
    Takes in a path to a zip file, and reads its contents
    :param path:
        path to the zip file
    :return: None
    """

    # Open the zip file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        # List all files in the zip archive
        file_list = zip_ref.namelist()

        # Iterate through each file in the zip archive
        for file_name in file_list:
            # Check if the file is a JSON file (you can customize this condition)
            if file_name.endswith('.json'):
                # Read the JSON content directly from the zip archive
                with zip_ref.open(file_name) as json_file:
                    # Load JSON content
                    json_data = json.load(json_file)
                    soup = BeautifulSoup(json_data, "html.parser")
                    # allText = soup.get_text()
                    # print(allText)

                    # exclude the title tag





def invertedIndex(files):
    userSearch = input('Search: ')
    tokens = re.findall(r'\w+', userSearch.lower(), flags=re.ASCII)

    ps = PorterStemmer()
    stemmedTokens = list(map(lambda token: ps.stem(token), tokens))




if __name__ == "__main__":

    stats = indexStats()

    zip_file_path = 'developer.zip'
    readZip(zip_file_path)
    print(stats.numDocs)
