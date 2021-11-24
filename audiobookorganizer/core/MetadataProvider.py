from abc import ABC, abstractmethod


class MetadataProvider(ABC):

    _APIURL = ""

    def __init__(self, api_key="", lang="de"):
        self.api_key = api_key
        self.lang = lang

    def setApiKey(self, key):
        self.api_key = key

    def setSearchLanguage(self, lang):
        self.lang = lang

    @abstractmethod
    def search(self, q=None, author=None, title=None, isbn=None, lang=None, show_preorders=True):
        pass
