import json

import requests
from requests.utils import requote_uri

from audiobookorganizer.core.AudioBookResult import AudioBookResult
from audiobookorganizer.core.MetadataProvider import MetadataProvider

from audiobookorganizer.core.Utils import get_series_from_googlebooks

import urllib


class Provider(MetadataProvider):
    _APIURL = 'https://www.googleapis.com/books/v1'

    def __init__(self, api_key="", lang="de"):
        super(Provider, self).__init__(api_key, lang)

    """
    """

    def _get(self, path, params=None):
        if params is None:
            params = {}
        else:
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
        resp = urllib.request.urlopen(self._APIURL + path + command)

        print("call to: " + self._APIURL + path + command)
        # resp = requests.get(self._APIURL + path + requests.utils.quote(command))
        # resp = requests.utils.quote(self._APIURL + path + command)
        # 'test%2Buser%40gmail.com'



        if resp.getcode() == 200:
            return json.loads(resp.read())

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

    def _build_search_string(self, q="", author=None, title=None, isbn=None):
        author = urllib.parse.quote(str(author))
        title = urllib.parse.quote(str(title))

        q += "" if author is None else f'+inauthor:"{author}"' if len(q) > 0 else f'inauthor:"{author}"'

        q += "" if title is None else f'+intitle:"{title}"' if len(q) > 0 else f'intitle:"{title}"'

        q += "" if isbn is None else f'+isbn:{isbn}' if len(q) > 0 else f'isbn:{isbn}'

        print(f'Search String={q}')

        return q

    def search(self, q="", author=None, title=None, isbn=None, lang=None, show_preorders=False, getfirst=False, grabseries=True):
        if lang is None:
            lang = self.lang

        kwargs = {}
        if lang: kwargs["langRestrict"] = lang
        if show_preorders: kwargs["showPreorders"] = show_preorders

        results = self._get_results(
            self._build_search_string(q=q, author=author, title=title, isbn=isbn),
            args=kwargs
        )

        if results["totalItems"] > 0:
            books = []
            if not getfirst:
                for item in results["items"]:
                    books.append(AudioBookResult.from_googlebooks(item))

                    return books
            else:
                book = None

                for item in results["items"]:
                    if item['saleInfo']['saleability'] != 'NOT_FOR_SALE':
                        book = AudioBookResult.from_googlebooks(item)

                if book is None:
                    book = AudioBookResult.from_googlebooks(results["items"][0])

                seriesInfo = get_series_from_googlebooks(book._rawData['id'])
                book.set('series', seriesInfo['series'])
                book.set('volume', seriesInfo['volume'])

                return book
        else:
            return list()
