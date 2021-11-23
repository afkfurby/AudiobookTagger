# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import googlebooks
from pprint import pprint
import os

def googleapi():

    api = googlebooks.Api()
    list = api.list('intitle:ich bin+inauthor:Dennis E. Taylor', langRestrict="de")

    print(f'Found {list["totalItems"]} items')

    if list["totalItems"] == 1:
        print(f'Title: {list["items"][0]["volumeInfo"]["title"]}')
        print(f'Author: {list["items"][0]["volumeInfo"]["authors"][0]}')
        print(f'Description: {list["items"][0]["volumeInfo"]["categories"]}')
        print(f'Description: {list["items"][0]["volumeInfo"]["description"]}')
        print(f'ISBN_13: {list["items"][0]["volumeInfo"]["industryIdentifiers"][0]["identifier"]}')
        print(f'Cover: {list["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]}')
    else:
        for item in list["items"]:
            # print(f'Title: {item["items"][0]["volumeInfo"]["title"]}')
            # print(f'Author: {item["items"][0]["volumeInfo"]["authors"][0]}')
            # print(f'Description: {item["items"][0]["volumeInfo"]["description"]}')
            # print(f'ISBN_13: {item["items"][0]["volumeInfo"]["industryIdentifiers"][0]["identifier"]}')
            # print(f'Cover: {item["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]}')
            pprint(item)

    # for item in list['items']:
    #     print(item)


def goodreads():
    from goodreads import client
    gc = client.GoodreadsClient( "", "")
    book = gc.book(1)
    print(book)

def audible():
    import audible

    # Authorize and register in one step
    auth = audible.Authenticator.from_login(
        "furbyhaxx@gmail.com",
        "4FK.studio$",
        locale="DE",
        with_username=True
    )

    # Save credendtials to file
    auth.to_file("data/audible.auth")

    # auth = audible.Authenticator.from_file(filename)
    client = audible.Client(auth)
    country_codes = ["de", "us", "ca", "uk", "au", "fr", "jp", "it", "in"]

    for country in country_codes:
        client.switch_marketplace(country)
        library = client.get("library", num_results=1000)
        asins = [book["asin"] for book in library["items"]]
        print(f"Country: {client.marketplace.upper()} | Number of books: {len(asins)}")
        print(34 * "-")


def tagread(file=None):
    import music_tag

    tags = [
        "album",
        "albumartist",
        "artist",
        "artwork",
        "comment",
        "compilation",
        "composer",
        "discnumber",
        "genre",
        "lyrics",
        "totaldiscs",
        "totaltracks",
        "tracknumber",
        "tracktitle",
        "year",
        "isrc",
    ]

    f = music_tag.load_file(file)

    for tag in tags:
        print(f'{ tag }: { f[tag] }')

    # print(f["artist"])
    # print(f["album"])
    # print(f["title"])
    # print(f["composer"])
    # print("lyrics")
    # print(f["lyrics"])
    # print("comment")
    # print(f["comment"])
    # pprint(f)


def has_subfolders(path_to_parent):
    num_folders = 0
    try:
        num_folders = len( next(os.walk(path_to_parent))[1] )
        if num_folders != 0:
            return True
    except StopIteration:
        return False


def filetype(file):
    import mimetypes

    mt = mimetypes.guess_type(file)
    #print(mt)
    if mt and mt[0] is not None:
        return tuple(mt[0].split("/"))
    else:
        return (os.path.splitext(file)[1], None)

def iterate():
    path = '\\\\10.1.1.210\media\\audio\\audio_books'

    import os
    # path = "./TEST"

    for root, d_names, f_names in os.walk(path):
        if not has_subfolders(root):
            print(d_names)
            for file in f_names:
                print(root, file)
                #print(filetype(file))
            # tagread(os.path.join(root))
            # print(root, d_names, f_names)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # googleapi()
    audible()
    # tagread("\\\\10.1.1.210\media\\audio\\audio_books\\Dennis E. Taylor\\Bobiverse\\Ich bin viele\\Ich bin viele Bobiverse 1 - 001.mp3")
    # tagread("data/Kapitel 1.m4b")
    # iterate()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
