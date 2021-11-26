import os
import re
import sys
import mimetypes
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
def has_subfolders(path_to_parent):
    try:
        num_folders = len(next(os.walk(path_to_parent))[1])
        if num_folders != 0:
            return True
    except StopIteration:
        return False


def get_filetype(file):
    mt = mimetypes.guess_type(file)

    audiotypes = ["m4b"]

    filename, file_extension = os.path.splitext(file)


    if mt and mt[0] is not None:
        return tuple(mt[0].split("/"))
    else:
        if mt is not None:
            # return os.path.splitext(file)[1], None
            if file_extension[1:] in audiotypes:
                return ("audio", file_extension[1:])
            else:
                return (None, None)
    return (None, None)


def get_folders_from_path(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts

def get_first_audio_file(root, files):
    for file in files:
        if get_filetype(os.path.join(root, file))[0] == "audio":
            return file
            break

def get_series_from_googlebooks(id):
    try:
        page = urlopen("https://books.google.ch/books?id=" + id)
    except:
        print("Error opening the URL")

    soup = BeautifulSoup(page, 'html.parser')

    # content = soup.find('a', {"class": "story-body sp-story-body gel-      body-copy"})

    content = soup.find("a", href=re.compile(r"bibliogroup"))
    # test2 = soup.find_all("a", href=lambda href: href and "bibliogroup" in href)
    # test3 = soup.select('a[href*="bibliogroup"]')

    elements = content.findAll('span')

    # for i in content.findAll('span'):
    #     print(i.text.split(" von "))
    if len(elements) > 0:
        element = content.findAll('span')[0]
        # parts = re.split('( [a-z]* )', element.text, 1)
        volume, trash, series = re.split('( [a-z]* )', element.text, 1)
        del trash
        volume = volume.split(" ")[1]


    return {
        "volume": volume,
        "series": series,
    }
