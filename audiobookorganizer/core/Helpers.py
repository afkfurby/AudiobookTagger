from collections import UserDict, namedtuple
import os
import music_tag
from music_tag.file import TAG_MAP_ENTRY, Artwork

from audiobookorganizer.metadata.GoogleBooks import Provider as GoogleBooksProvider


"""
MetadataDict
from audiobookorganizer.core.Helpers import MetadataDict
# MetadataDict({})
meta = MetadataDict({"Title": "Original Title", "Author": "Furby Haxx"})
"""
# TAG_MAP_ENTRY = namedtuple('TAG_MAP_ENTRY', ('getter', 'setter', 'remover',
#                                              'type', 'sanitizer'))

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

    _DEFAULTS = dict({
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

    def __init__(self, val=None):
        defaults = MetadataDict._DEFAULTS.copy()

        if val is not None:
            defaults.update(val)

        super().__init__(defaults)
        self._changed = False

    def __getattr__(self, attr: str) -> str:
        return self.__getitem__(attr)

    def __setattr__(self, attr: str, val: str) -> None:
        # print(attr)
        if attr in ['store', 'data', '_changed']:
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
        if item in super().keys(): # key exists
            if super().__getitem__(item) is None:  # not set yet
                self._changed = True
                super().__setitem__(item, value)
            elif item in ["Genres", "Cover"]:
                if isinstance(super().__getitem__(item), list):
                    if isinstance(value, list):
                        self._changed = True
                        super().__setitem__(item, super().__getitem__(item) + value)
                    else:
                        self._changed = True
                        super().__setitem__(item, super().__getitem__(item).append(value))
                else:
                    self._changed = True
                    super().__setitem__(item, [super().__getitem__(item)] + value)

                self._changed = True
        else:
            self._changed = True
            super().__setitem__(item, value)

    def override(self, item, value):
        if item in super().keys():  # existing key
            self._changed = True
            super().__setitem__(item, value)

    def __delitem__(self, item):
        super().__delitem__(item)
        self._changed = True

    # def __getitem__(self, key):
    #     if key in self.data:
    #         return self.data[key]
    #     if hasattr(self.__class__, "__missing__"):
    #         return super().__class__.__missing__(self, key)
    #     raise KeyError(key)

    def _getimage(self, item):
        if isinstance(item, Artwork):
            return item.image
        else:
            return item


    def has_changed(self):
        return self._changed

    def export_cover(self, path, index=0, case_sensitive=False):
        # f['artwork'].first.image.save("./data/cover.jpg")
        if super().__getitem__("Cover") is not None:
            if len(super().__getitem__("Cover")) == 1:
                self._getimage(super().__getitem__("Cover")).save(os.path.join(path, "cover.jpg"))
                if case_sensitive:
                    self._getimage(super().__getitem__("Cover")).save(os.path.join(path, "Cover.jpg"))

                return True
            else:
                self._getimage(super().__getitem__("Cover")[index]).save(os.path.join(path, "cover.jpg"))
                if case_sensitive:
                    self._getimage(super().__getitem__("Cover")[index]).save(os.path.join(path, "Cover.jpg"))

                return True

        return False

    @staticmethod
    def from_googlebooks(author, title):
        metadataprovider = GoogleBooksProvider()
        result = metadataprovider.search(author=author, title=title,
                                               getfirst=True, rawresult=True)

        from datetime import datetime
        from PIL import Image
        from io import BytesIO
        import requests
        response = requests.get(result["volumeInfo"]["imageLinks"]["thumbnail"])
        cover = Image.open(BytesIO(response.content))

        dt = datetime.strptime(result["volumeInfo"]["publishedDate"], '%Y-%m-%d')

        return MetadataDict({
            "Title": result["volumeInfo"]["title"],
            "Subtitle": result["volumeInfo"]["subtitle"],
            "Author": result["volumeInfo"]["authors"][0],
            # "Narrator": None,
            "Publisher": result["volumeInfo"]["publisher"],
            "Year": dt.year,
            "Description": result["volumeInfo"]["description"],
            "Genres": result["volumeInfo"]["categories"],
            "Series": result["volumeInfo"]["series"],
            "Volume": result["volumeInfo"]["volume"],
            "Cover": [cover],
            # "tracknumber": None,
            # "totaltracks": None,
            # "discnumber": None,
            # "totaldiscs": None,
            "isbn13": result["volumeInfo"]["industryIdentifiers"][0]["identifier"]
        })

    @staticmethod
    def from_file(file, defaults=None):
        if defaults is None:
            defaults = {}

        f = music_tag.load_file(file)

        default = MetadataDict._DEFAULTS.copy()

        for key, value in MetadataDict._TAGMAP.items():
            try:
                if key == "Cover":
                    default[key] = f[value].value
                else:
                    default[key] = f[value].value
            except:
                continue
            # if value in f:
            #     default[key] = f[value]

        defaults.update(default)
        meta = MetadataDict(defaults)
        meta['_File'] = f
        return meta

    def save_to_file(self, file=None):
        if file is None:
            if "_File" in super().keys():
                f = super().__getitem__("_File")
            else:
                pass # should throw error
        else:
            f = music_tag.load_file(file)

        for key in super().keys():
            if key not in ['store', 'data', '_changed', "_File"]:
                if super().__getitem__(key) is not None:

                    # TODO: find out how to write new tags to m4b file (eg. subtitle, isbn)
                    # if key not in f.tag_map:
                    #     if isinstance(super().__getitem__(key), int) or super().__getitem__(key).isnumeric():
                    #         f.tag_map[key.lower()] = TAG_MAP_ENTRY(getter='©nam', setter='©nam', type=int)
                    #     else:
                    #         f.tag_map[key.lower()] = TAG_MAP_ENTRY(getter='©nam', setter='©nam', type=str)
                    if key in f.tag_map:
                        f[MetadataDict._TAGMAP[key]] = super().__getitem__(key)

        f.save()


