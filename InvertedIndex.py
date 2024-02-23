from dataclasses import dataclass
import zipfile

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
    with zipfile.ZipFile(path, 'r') as zip_file:
        file_list = zip_file.namelist()
        for file_name in file_list:
            with zip_file.open(file_name) as file:
                stats.numDocs+=1


if __name__ == "__main__":
    stats = indexStats()
    readZip("developer.zip")

    print(stats.numDocs)


