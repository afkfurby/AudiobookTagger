import json

import requests
import urllib3
from requests.utils import requote_uri

from audiobookorganizer.core.AudioBookResult import AudioBookResult
from audiobookorganizer.core.MetadataProvider import MetadataProvider

from audiobookorganizer.core.Utils import get_series_from_googlebooks

import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

import cli_ui as ui

class Provider(MetadataProvider):
    _APIURL = 'https://www.googleapis.com/books/v1'

    def __init__(self, api_key="AIzaSyC016ESjNILKeicAj3bPUKmOHYLqBxiDv0", lang="de"):
        ui.setup(color="always")
        self._APIKEY = api_key
        super(Provider, self).__init__(api_key, lang)

        # api info

    """
    """

    def _get(self, path, params=None):
        if params is None:
            params = {
                "key": self._APIKEY
            }
        else:
            params['key'] = self._APIKEY
            command = "?"
            first = True
            for key, value in params.items():
                if first:
                    command += f'{key}={value}'
                    first = False
                else:
                    command += f'&{key}={value}'


        # resp = requests.get(self._APIURL + path + command)
        # import urllib.request
        # resp = urllib.request.urlopen(self._APIURL + path + command)

        http = urllib3.PoolManager()
        # resp = http.request("GET", self._APIURL + path + command)

        # http.urlopen("")

        resp = http.urlopen(
            "GET",
            self._APIURL + path + command
        )
        # resp = http.urllib3.request(
        #     "GET",
        #     self._APIURL + path,
        #     fields={
        #         "q": 'intitle:Totengräber',
        #     }
        # )

        # print("call to: " + self._APIURL + path + command)
        ui.debug("GB Call to:", ui.bold, self._APIURL + path + command)
        # resp = requests.get(self._APIURL + path + requests.utils.quote(command))
        # resp = requests.utils.quote(self._APIURL + path + command)
        # 'test%2Buser%40gmail.com'



        if resp.status == 200:
            return json.loads(resp.data.decode('utf8'))

        return resp

    def _get_results(self, q, args={}, **kwargs):
        """Performs a book search.

        q -- Full-text search query string.

            There are special keywords you can specify in the search terms to
            search in particular fields, such as:

            intitle: Returns results where the text following this keyword is
                    found in the title.
            inauthor: Returns results where the text following this keyword is
                    found in the author.
            inpublisher: Returns results where the text following this keyword
                    is found in the publisher.
            subject: Returns results where the text following this keyword is
                    listed in the category list of the volume.
            isbn:   Returns results where the text following this keyword is the
                    ISBN number.
            lccn:   Returns results where the text following this keyword is the
                    Library of Congress Control Number.
            oclc:   Returns results where the text following this keyword is the
                    Online Computer Library Center number.

        Optional Parameters:

        download -- Restrict to volumes by download availability.

                    Acceptable values are:
                    "epub" - All volumes with epub.

        filter --   Filter search results.

                    Acceptable values are:
                    "ebooks" - All Google eBooks.
                    "free-ebooks" - Google eBook with full volume text viewability.
                    "full" - Public can view entire volume text.
                    "paid-ebooks" - Google eBook with a price.
                    "partial" - Public able to see parts of text.

        langRestrict -- Restrict results to books with this language code.

        libraryRestrict	-- Restrict search to this user's library.

                    Acceptable values are:
                    "my-library" - Restrict to the user's library, any shelf.
                    "no-restrict" - Do not restrict based on user's library.

        maxResults -- Maximum number of results to return. Acceptable values are 0 to 40, inclusive.

        orderBy	 -- Sort search results.

                    Acceptable values are:
                    "newest" - Most recently published.
                    "relevance" - Relevance to search terms.

        partner	--  Restrict and brand results for partner ID.

        printType -- Restrict to books or magazines.

                    Acceptable values are:
                    "all" - All volume content types.
                    "books" - Just books.
                    "magazines" - Just magazines.

        projection -- Restrict information returned to a set of selected fields.

                    Acceptable values are:
                    "full" - Includes all volume data.
                    "lite" - Includes a subset of fields in volumeInfo and accessInfo.

        showPreorders -- Set to true to show books available for preorder. Defaults to false.

        source --  String to identify the originator of this request.

        startIndex -- Index of the first result to return (starts at 0)

        See: https://developers.google.com/books/docs/v1/reference/volumes/list
        """
        path = '/volumes'
        params = dict(q=q)
        for p in 'download filter langRestrict libraryRestrict maxResults orderBy partner printType projection showPreorders source startIndex'.split():
            if p in args:
                params[p] = args[p]

        return self._get(path, params)

    def _quote(self, string):
        return string.replace(" ", "%20")

    def _build_search_string(self, q="", author=None, title=None, isbn=None):
        # author = urllib.parse.quote(str(author))
        # title = urllib.parse.quote(str(title))

        author = u'' + self._quote(author) # custom quote (only whitespace) because every library fucks something up
        title = u'' + self._quote(title)

        author = author.encode("utf-8")
        title = title.encode("utf-8")

        q += "" if author is None else f'+inauthor:"{author.decode()}"' if len(q) > 0 else f'inauthor:"{author.decode()}"'

        q += "" if title is None else f'+intitle:"{title.decode()}"' if len(q) > 0 else f'intitle:"{title.decode()}"'

        q += "" if isbn is None else f'+isbn:{isbn}' if len(q) > 0 else f'isbn:{isbn}'

        # print(f'Search String={q}')

        return q

    def _get_series_from_googlebooks(self, bookid):
        try:
            page = urlopen("https://books.google.ch/books?id=" + bookid)
        except:
            print("Error opening the URL")

        soup = BeautifulSoup(page, 'html.parser')

        # content = soup.find('a', {"class": "story-body sp-story-body gel-      body-copy"})

        content = soup.find("a", href=re.compile(r"bibliogroup"))
        # test2 = soup.find_all("a", href=lambda href: href and "bibliogroup" in href)
        # test3 = soup.select('a[href*="bibliogroup"]')

        if content is not None:
            elements = content.findAll('span')
        else:
            volume, series = None, None

        # for i in content.findAll('span'):
        #     print(i.text.split(" von "))
        if content is not None and len(elements) > 0:
            element = content.findAll('span')[0]
            # parts = re.split('( [a-z]* )', element.text, 1)
            volume, trash, series = re.split('( [a-z]* )', element.text, 1)
            del trash
            vtmp = volume.split(" ")[1]
            volume = int(vtmp) if vtmp.isnumeric() else 0

        return {
            "volume": volume,
            "series": series,
        }

    def search(self, q="", author=None, title=None, isbn=None, lang=None, show_preorders=False, getfirst=False, grabseries=True, rawresult=False):
        if lang is None:
            lang = self.lang

        self._title = title

        kwargs = {}
        if lang: kwargs["langRestrict"] = lang
        if show_preorders: kwargs["showPreorders"] = show_preorders

        # results = self._get_results(
        #     self._build_search_string(q=q, author=author, title=title, isbn=isbn),
        #     args=kwargs
        # )
        results = self._get_results(
            self._build_search_string(q=q, author=author, title=title, isbn=isbn),
            args=kwargs
        )

        if results["totalItems"] == 0:  # nothing found, try improving
            author = author  # this should always be correct
            title_fragments = title.split(" ")

            for i in range(len(title_fragments)):
                ql = list()
                ql.append(title_fragments.pop())

                results = self._get_results(
                    self._build_search_string(q=self._join(ql), author=author, title=self._join(title_fragments), isbn=isbn),
                    args=kwargs
                )

                if results["totalItems"] > 0:
                    break

        if results["totalItems"] > 0:
            return self._handle_results(results, getfirst, rawresult)
            # books = []
            # if not getfirst:
            #     if not rawresult:
            #         for item in results["items"]:
            #             books.append(AudioBookResult.from_googlebooks(item))
            #
            #         return books
            #     else:
            #         return results["items"]
            # else:
            #     book = None
            #
            #     if not rawresult:
            #         for item in results["items"]:
            #             if item['saleInfo']['saleability'] != 'NOT_FOR_SALE':
            #                 book = AudioBookResult.from_googlebooks(item)
            #
            #         if book is None:
            #             book = AudioBookResult.from_googlebooks(results["items"][0])
            #
            #         seriesInfo = self._get_series_from_googlebooks(book._rawData['id'])
            #         book.set('series', seriesInfo['series'])
            #         book.set('volume', seriesInfo['volume'])
            #
            #         return book
            #     else:
            #         for item in results["items"]:
            #             if item['saleInfo']['saleability'] != 'NOT_FOR_SALE':
            #                 series_info = self._get_series_from_googlebooks(item['id'])
            #                 item["volumeInfo"]["series"] = series_info['series']
            #                 item["volumeInfo"]["volume"] = series_info['series']
            #                 return item
        else:
            if lang != "en":
                lang = "en"
                return self.search(q, author, title, isbn, lang, show_preorders, getfirst, grabseries, rawresult)
            else:
                return None

    def _join(self, l, s=" "):
        if isinstance(l, list):
            return s.join(l)
        else:
            return l

    def _handle_results(self, results, getfirst, rawresult):
        # TODO: fix this
        books = []
        if not getfirst:
            if not rawresult:
                for item in results["items"]:
                    books.append(AudioBookResult.from_googlebooks(item))

                return books
            else:
                return results["items"]
        else:
            book = None

            if not rawresult:
                for item in results["items"]:
                    if item['saleInfo']['saleability'] != 'NOT_FOR_SALE':
                        book = AudioBookResult.from_googlebooks(item)

                if book is None:
                    book = AudioBookResult.from_googlebooks(results["items"][0])

                seriesInfo = self._get_series_from_googlebooks(book._rawData['id'])
                book.set('series', seriesInfo['series'])
                book.set('volume', seriesInfo['volume'])

                return book
            else:
                if len(results["items"]) > 1:
                    for item in results["items"]:
                        if item['saleInfo']['saleability'] != 'NOT_FOR_SALE':
                            series_info = self._get_series_from_googlebooks(item['id'])
                            item["volumeInfo"]["series"] = series_info['series']
                            item["volumeInfo"]["volume"] = series_info['volume']
                            return item
                else:
                    from difflib import SequenceMatcher
                    def similar(a, b):
                        return SequenceMatcher(None, a, b).ratio()

                    best_match_ratio = 0.0
                    best_match = None

                    for item in results["items"]:
                        ratio = similar(item["volumeInfo"]["title"], self._title)
                        if ratio > best_match_ratio:
                            best_match_ratio = ratio
                            best_match = item

                    series_info = self._get_series_from_googlebooks(best_match['id'])
                    best_match["volumeInfo"]["series"] = series_info['series']
                    best_match["volumeInfo"]["volume"] = series_info['series']
                    return best_match

