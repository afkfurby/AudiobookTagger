from collections import UserDict

"""
MetadataDict
from audiobookorganizer.core.Helpers import MetadataDict
# MetadataDict({})
meta = MetadataDict({"Title": "Original Title", "Author": "Furby Haxx"})
"""
class MetadataDict(UserDict):

    _TAGMAP = {
        "Author": "artist",
        "Title": "tracktitle",
        "Subtitle": "subtitle",
        "Publisher": "publisher",
        "Year": "year",
        "Narrator": "composer",
        "Description": ["description", "comment"],
        "Genres": "genre",
        "Series": "series",
        "Volume": "series-part",
        "Cover": "artwork",
        "tracknumber": "tracknumber",
        "totaltracks": "totaltracks",
        "discnumber": "discnumber",
        "totaldiscs": "totaldiscs",

    }

    def __init__(self, val=None):
        defaults = dict({
            "Title": None,
            "Subtitle": None,
            "Author": None,
            "Narrator": None,
            "Publisher": None,
            "Year": None,
            "Description": None,
            "Genres": None,
            "Series": None,
            "Volume": None,
            "Cover": None,
            "tracknumber": None,
            "totaltracks": None,
            "discnumber": None,
            "totaldiscs": None,
        })
        if val is not None:
            defaults.update(val)

        super().__init__(defaults)
        self._changed = False

    def __getattr__(self, attr: str) -> str:
        return self.__getitem__(attr)

    def __setattr__(self, attr: str, val: str) -> None:
        # print(attr)
        if attr == 'store' or attr == 'data':
            super().__setattr__(attr, val)
        else:
            self.__setitem__(attr, val)

    def __delattr__(self, key):
        try:
            self.__delitem__(key)
        except KeyError as k:
            raise AttributeError(k)

    # def __repr__(self):
    #     return '<MetadataDict ' + super.__repr__(self) + '>'

    def __setitem__(self, item, value):
        if item in super().keys():
            if super().__getitem__(item) is None:  # not set yet
                self.changed = True
                super().__setitem__(item, value)
        else:
            self.changed = True
            super().__setitem__(item, value)


    def override(self, item, value):
        if item in super().keys():  # existing key
            self.changed = True
            super().__setitem__(item, value)

    def __delitem__(self, item):
        super().__delitem__(item)
        self.changed = True

    def hasChanged(self):
        return self.changed
