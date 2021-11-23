# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import googlebooks
from pprint import pprint

def test():

    api = googlebooks.Api()
    list = api.list('intitle:universum+inauthor:Peterson', langRestrict="de")

    print(f'Found {list["totalItems"]} items')

    if list["totalItems"] == 1:
        print(f'Title: { list["items"][0]["volumeInfo"]["title"] }')
        print(f'Author: {list["items"][0]["volumeInfo"]["authors"][0]}')
        print(f'Description: {list["items"][0]["volumeInfo"]["description"]}')
        print(f'ISBN_13: {list["items"][0]["volumeInfo"]["industryIdentifiers"][0]["identifier"]}')
        print(f'Cover: {list["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]}')

    # for item in list['items']:
    #     print(item)




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    test()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
