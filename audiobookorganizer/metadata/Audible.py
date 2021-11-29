import json


import urllib3


from audiobookorganizer.core.AudioBookResult import AudioBookResult
from audiobookorganizer.core.MetadataProvider import MetadataProvider


from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import datetime

import cli_ui as ui

class Provider(MetadataProvider):
    _INTL_SITES = {
        'en': {
            'url': 'www.audible.com',
            'urltitle': u'title=',
            'rel_date': u'Release date',
            'nar_by': u'Narrated By',
            'nar_by2': u'Narrated by',
            'datestr': '%Y-%m-%d'
            # series text Bobiverse, Book 2
        },
        'fr': {
            'url': 'www.audible.fr',
            'urltitle': u'title=',
            'rel_date': u'Date de publication',
            'nar_by': u'Narrateur(s)',
            'nar_by2': u'Lu par'
        },
        'de': {
            'url': 'www.audible.de',
            'urltitle': u'title=',
            'author': u'Von',
            'rel_date': u'Erscheinungsdatum: ',
            'nar_by': u'Gesprochen von',
            'rel_date2': u'Veröffentlicht',
            'datestr': '%d.%m.%Y'
        },
        'it': {
            'url': 'www.audible.it',
            'urltitle': u'title=',
            'rel_date': u'Data di Pubblicazione',
            'nar_by': u'Narratore'
        },
    }

    _SITE_LANGS = {
        'www.audible.com': {'lang': 'en'},
        'www.audible.ca': {'lang': 'en'},
        'www.audible.co.uk': {'lang': 'en'},
        'www.audible.com.au': {'lang': 'en'},
        'www.audible.fr': {'lang': 'fr'},
        'www.audible.de': {'lang': 'de'},
        'www.audible.it': {'lang': 'it'},
    }

    _SEARCH_URL = "/search?keywords="


    _APIURL = 'https://www.googleapis.com/books/v1'

    def __init__(self, api_key="", lang="de"):
        ui.setup(color="always")
        super(Provider, self).__init__(api_key, lang)

    def _set_api_url(self, lang):
        Provider._APIURL = Provider._INTL_SITES[lang]['url'] + Provider._SEARCH_URL

    def _get_child(self, soup, tag, search):
        return soup.find(tag, search)
        # for child in soup.children:
            # if child.name == tag:
            #     return child

    def _image_from_url(self, url):
        from PIL import Image
        import requests
        from io import BytesIO

        response = requests.get(url)
        return Image.open(BytesIO(response.content))

    def _cleanup_list(self, input):
        newlist = []
        for i in input:
            if len(i) > 0:
                newlist.append(i.replace("\n", ""))
        return newlist

    def _parse_search_results(self, content):
        soup = BeautifulSoup(content, 'html.parser')

        num_results = soup.find("span", {"class": "resultsSummarySubheading"})

        results = {
            "totalResults": 0,
            "items": []
        }

        for f in num_results.text.split(" "):
            if f.isnumeric():
                results["totalResults"] = int(f)

        items = soup.findAll("li", {"class": "productListItem"})

        for item in items:
            # heading = item.find("h3", {"class": "bc-heading"})
            # for c in heading.children:
            #     if c.name == "a":
            #         title = c.text

            title = item.find("h3", {"class": "bc-heading"}).select_one("a").text
            # title, subtitle = title.split(": ") if title.find(": ") else title, ""

            subtitle = item.find("li", {"class": "subtitle"})
            if subtitle is not None:
                subtitle = subtitle.select_one("span").text
                subtitle = subtitle.split(" ")
                volume = int(subtitle.pop()) if subtitle[-1].isnumeric() else None
                series = " ".join(subtitle)
            else:
                series = None
                volume = None


            author = item.select_one("a[href*=uthor]").text

            # TODO: Implement grabbing book description from audible (link to book page in title)

            results['items'].append({
                "title": title,
                # "subtitle": "" if subtitle is None else subtitle,
                "author": author,
                "series": series,
                "volume": volume,
                "narrator": item.select_one("a[href*=searchNarrator]").text,
                "release_date": datetime.datetime.strptime(
                    self._cleanup_list(item.find("li", {"class": "releaseDateLabel"}).select_one("span").text.split(" "))[-1],
                    self._INTL_SITES[self.lang]['datestr']),
                "language": self._cleanup_list(item.find("li", {"class": "languageLabel"}).select_one("span").text.split(" "))[-1],
                "cover": self._image_from_url(item.find("img", {"class": "bc-pub-block"}).attrs['src'])
            })

        return results

    def search(self, q="", author="", title="", isbn="", lang="", show_preorders="", getfirst="", grabseries="", rawresult=""):

        if lang is None:
            lang = self.lang

        self._set_api_url(self.lang)

        http = urllib3.PoolManager()
        resp = http.urlopen(
            "GET",
            Provider._APIURL + q + "&title=" + title + "&author_author=" + author
        )
        ui.debug(Provider._APIURL + q + "&title=" + title + "&author_author=" + author)
        # print(Provider._APIURL + q + "&title=" + title + "&author_author=" + author)
        # resp = http.request(
        #     "GET",
        #     self.url,
        #     fields={
        #         "keywords": q,
        #         "title": title,
        #         "author_author": author,
        #         "narrator": narrator,
        #         "publisher": publisher
        #     }
        # )

        if resp.status == 200:
            data = resp.data.decode('utf8')

            results = self._parse_search_results(data)

            return results

