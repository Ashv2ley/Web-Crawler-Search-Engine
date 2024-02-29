import zipfile
import json
from urllib.parse import urlparse

from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup
from dataclasses import dataclass,field
from collections import Counter
import re
from collections import defaultdict
from typing import DefaultDict, List, Set


@dataclass
class indexStats():
    """
    Class that keeps track of all the stats of the index
    """
    numDocs: int = 0
    uniquePages: int = 0
    totalSize: int = 0
    indexDict: DefaultDict[str, List] = field(default_factory = lambda: defaultdict(list))
    uniqueTokens: Set[str] = field(default_factory = set)

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
        # elif "Table:" in line:
        #     sorted_index = dict(sorted(stats.indexDict.items()))
        #     for key, val in sorted_index.items():
        #         lines[i] += f"{key}: {val}\n"

    with open("report.txt", "w") as report:
        report.writelines(lines)

def readZip(path:str):
    """
    Takes in a path to a zip file, and reads its contents
    :param path:
        path to the zip file
    :return: None
    """

    count = 0
    # Open the zip file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
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
                    alpha = [word.lower() for word in alphanumeric_words]
                    counter = Counter(alpha)
                    #gets each word and frequency in each file
                    for word, count in counter.items():
                        ps = PorterStemmer()
                        stemmedWord = ps.stem(word)
                        stats.uniqueTokens.add(stemmedWord)
                        stats.indexDict[stemmedWord].append((json_data['url'], count))
        writeReport()



if __name__ == "__main__":

    stats = indexStats()
    zip_file_path = 'developer.zip'
    readZip(zip_file_path)
