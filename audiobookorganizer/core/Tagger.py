
import music_tag


class FileMetadata:

    TAGMAP = {
        "author": "artist",
        "title": "tracktitle",
        "subtitle": "subtitle",
        "publisher": "publisher",
        "year": "year",
        "narrator": "composer",
        "description": ["description", "comment"],
        "genres": "genre",
        "series": "series",
        "volume": "series-part",
        "cover": "artwork",
        "tracknumber": "tracknumber",
        "totaltracks": "totaltracks",
        "discnumber": "discnumber",
        "totaldiscs": "totaldiscs",

    }

    UPDATABLE_TAGS = ["author", "title", "subtitle", "publisher", "year", "narrator", "description", "genres", "series", "volume"]

    def __init__(self, filepath):
        self.file = music_tag.load_file(filepath)
        self.new_metadata = {}
        for tag in FileMetadata.UPDATABLE_TAGS:
            self.new_metadata[tag] = self.get(tag)

    def _check_missing_tags(self):
        for key, value in self.TAGMAP.items():
            print(self.file[value])

    def update(self, tagname, value):

        if value is not None or str(value) != "":
            if self._get(tagname) is None or str(self._get(tagname)) == "":
                if isinstance(value, list):
                    if tagname == "author":
                        self.set(tagname, value[0])
                    elif tagname == "genres":
                        genres = self._get(tagname)
                        for item in value:
                            genres += ";" + item

                        self.set(tagname, genres)
            else:
                self.set(tagname, value)



    def set(self, tagname, value):
        self.new_metadata[tagname] = value

    def _get(self, tagname):
        return self.new_metadata[tagname]

    def get(self, tagname):
        if tagname in FileMetadata.TAGMAP:
            # return self.file[FileMetadata.TAGMAP[tagname]]
            if isinstance(FileMetadata.TAGMAP[tagname], list):
                for tag in FileMetadata.TAGMAP[tagname]:
                    if tag in self.file.tag_map:
                        value = self.file[tag]
                        if value is not None or value == "":
                            return value
                return False

            if FileMetadata.TAGMAP[tagname] in self.file.tag_map:
                return self.file[FileMetadata.TAGMAP[tagname]]
            else:
                return None
        elif tagname in self.file:
            return self.file[tagname]
        else:
            return None


    def save(self):
        for key, value in self.new_metadata.items():
            self.file[key] = value

        self.file.save()