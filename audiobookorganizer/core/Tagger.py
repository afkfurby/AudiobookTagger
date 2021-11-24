
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

    def __init__(self, filepath):
        self.file = music_tag.load_file(filepath)

    def _check_missing_tags(self):
        for key, value in self.TAGMAP.items():
            print(self.file[value])

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


