from abc import ABCMeta, abstractmethod, ABC

import mutagen
from mutagen.id3 import ID3, TXXX, TPE1
from mutagen.id3._frames import TextFrame
from mutagen.mp4 import MP4, MP4FreeForm
import importlib
'''
from audiobookorganizer.core.Tagger import MP4Tag
from mutagen.mp4 import MP4
mp4filename = "data/Oberons blutige Fälle.m4b"
mp4tags = MP4(mp4filename)
t = MP4Tag("test", ["----:TXXX:TESTTAG"], mp4tags)

t = MP4Tag("author", ["©ART", "aART", "----:TXXX:AUTHOR"], mp4tags)
t = MP4Tag("author", ["----:TXXX:TESTTAG"], mp4tags)
'''


class AbstractBaseTag(metaclass=ABCMeta):

    def __init__(self, name="", tags=None, file=None, value=None):
        if tags is None:
            tags = []

        self.__name = name
        self.__tags = tags
        self.__value = value
        self.__file = file
        self.file = file
        self.value = value

    @property
    def name(self):
        return self.__name

    @property
    def tags(self):
        return self.__tags

    @property
    def file(self):
        return self.__file

    @file.setter
    def file(self, fileobj):
        self.__file = fileobj

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def set(self, value):
        pass

    def save(self):
        self.__file.save()

    def __str__(self):
        s = "BaseTag("
        s += ", ".join(self.__tags)
        s += " = "
        s += str(self.__value)
        s += ")"
        return s

    def __repr__(self):
        return self.__str__()


'''
from audiobookorganizer.core.Tagger import MP3Tag
from mutagen.id3 import ID3
mp3filename = "data/Die Kinder der Zeit.mp3"
mp3tags = ID3(mp3filename)
t = MP3Tag("author", ["TPE1", "TPE2", "TXXX:AUTHOR"], mp3tags)

'''
class MP3Tag(AbstractBaseTag, ABC):

    def __init__(self, name="", tags=None, file=None, value=None):
        if file is None:
            file = ID3()
        if tags is None:
            tags = []

        super().__init__(name, tags, file, value)

    def get(self):
        values = []
        for t in self.tags:
            if t in self.file.keys():
                try:
                    values.append(int(self.file[t]))
                except:
                    values.append(str(self.file[t]))
                # if isinstance(self.file[t], list):
                #     for tt in self.file[t]:
                #         # if isinstance(tt, bytes):
                #         #     values.append(bytes(tt).decode("utf-8"))
                #         # else:
                #         values.append(tt)
                # elif isinstance(self.file[t], MP4FreeForm):
                #     values.append(bytes(self.file[t]).decode("utf-8"))
                # else:
                # if isinstance(self.file[t], TextFrame):
                #     values.append(self.file[t])

        return values
        return list(set(values))

    def set(self, value):
        self.value = value

        for tag in self.tags:
            tagc = "TXXX" if str(tag).find(":") else tag
            mod = importlib.import_module('mutagen.id3')
            c = getattr(mod, tagc)

            if isinstance(value, int):
                self.file[tag] = c(encoding=3, text=value )
            else:
                self.file[tag] = c(encoding=3, text=u"" + value)
        '''
        import importlib
        mod = importlib.import_module('mutagen.id3')
        c = getattr(mod, "TXXX")
        '''


class MP4Tag(AbstractBaseTag, ABC):

    def __init__(self, name="", tags=None, file=None, value=None):
        if file is None:
            file = MP4()
        if tags is None:
            tags = []

        super().__init__(name, tags, file, value)

    def get(self):
        values = []
        for t in self.tags:
            if t in self.file.keys():
                if isinstance(self.file[t], list):
                    for tt in self.file[t]:
                        if isinstance(tt, bytes):
                            values.append(bytes(tt).decode("utf-8"))
                        else:
                            values.append(tt)
                elif isinstance(self.file[t], MP4FreeForm):
                    values.append(bytes(self.file[t]).decode("utf-8"))
                else:
                    values.append(self.file[t])

        return list(set(values))

    def set(self, value):
        self.value = value
        for t in self.tags:
            if t.startswith("----:"):  # freeform tag
                self.file[t] = bytes(self.value, "UTF-8")
            else:
                self.file[t] = self.value

    # def __str__(self):
    #     s = "MP4Tag("
    #     s += ", ".join(self.__tags)
    #     s += " = "
    #     s += self.__value
    #     s += ")"
    #     return s




class AudiobookMetadata:
    _TAGMAP = {
        "mp3": {
            "author": MP3Tag("author", ["TPE1", "TPE2", "TXXX:AUTHOR"]),
            "title": MP3Tag("title", ["TIT2", "TXXX:BOOKTITLE", "TXXX:TITLE"]),
            "series": MP3Tag("series", ["TALB", "TXXX:SERIES"]),
            "volume": MP3Tag("volume", ["TXXX:VOLUME"]),
            "year": MP3Tag("year", ["TORY", "TDRC"]),
            "cover": MP3Tag("cover", ["APIC"]),
            "narrator": MP3Tag("narrator", ["TCOM", "TXXX:NARRATEDBY", "TXXX:NARRATOR"]),
            "publisher": MP3Tag("publisher", ["TXXX:Publisher", "TXXX:PUBLISHER"]),
            "description": MP3Tag("description", ["COMM", "TXXX:DESCRIPTION"]),
            "genres": MP3Tag("genre", ["TCON"]),
            "diskinfo": MP3Tag("diskinfo", ["TPOS"]),
            "trackinfo": MP3Tag("trackinfo", ["TRCK"]),
            "isbn": MP3Tag("trackinfo", ["TXXX:ISBN"]),
            "asin": MP3Tag("trackinfo", ["TXXX:ASIN"]),
        },
        "mp4": {
            "author": MP4Tag("author", ["©ART", "aART", "----:TXXX:AUTHOR"]),
            "title": MP4Tag("title", ["©nam", "----:TXXX:TITLE"]),
            "series": MP4Tag("series", ["©alb", "----:TXXX:SERIES"]),
            "volume": MP4Tag("volume", ["----:TXXX:VOLUME"]),
            "year": MP4Tag("year", ["©day"]),
            "cover": MP4Tag("cover", ["covr"]),
            "narrator": MP4Tag("narrator", ["©wrt"]),
            "publisher": MP4Tag("publisher", ["----:TXXX:PUBLISHER", "cprt"]),
            "description": MP4Tag("description", ["desc", "©cmt", "----:TXXX:DESCRIPTION"]),
            "genre": MP4Tag("genre", ["©gen"]),
            "diskinfo": MP4Tag("diskinfo", ["disk"]),
            "trackinfo": MP4Tag("trackinfo", ["trkn"]),
            "isbn": MP4Tag("trackinfo", ["----:TXXX:ISBN"]),
            "asin": MP4Tag("trackinfo", ["----:TXXX:ASIN"]),
        }
    }

    def __init__(self):
        pass

    def set_isbn(self, filename, isbn):
        if filename.lower().endswith(".mp3"):
            tags = ID3(filename)
            tags.add(TXXX(encoding=3, desc=u'ISBN', text=str(isbn)))
            tags.save(filename)
        else:
            tags = MP4(filename)
            tags["----:TXXX:ISBN"] = bytes(isbn, 'UTF-8')
            tags.save(filename)
