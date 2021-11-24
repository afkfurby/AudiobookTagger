from datetime import datetime

class AudioBookResult:

    def __init__(self, title, author, description, categories, isbn, cover, all_authors=[], subtitle="", publisher="", publishedDate="", series="", volume="", rawData={}):
        self.title = title
        self.author = author
        self.authors = all_authors
        self.description = description
        self.categories = categories
        self.isbn = isbn
        self.cover = cover

        self.subtitle = subtitle
        self.publisher = publisher
        self.publishedDate = publishedDate

        self.series = series
        self.volume = volume

        self._rawData = rawData

        self._dict = {
            "author": author,
            "title": title,
            "subtitle": subtitle,
            "publisher": publisher,
            "year": publishedDate,
            # "narrator": "composer",
            "description": description,
            "genres": categories,
            "series": series,
            "volume": volume,
            "cover": cover,
            # "tracknumber": "tracknumber",
            # "totaltracks": "totaltracks",
            # "discnumber": "discnumber",
            # "totaldiscs": "totaldiscs",
        }

    def set(self, key, value):
        self._dict[key] = value
        setattr(self, key, value)

    @staticmethod
    def from_googlebooks(result):
        from datetime import datetime

        dt = datetime.strptime(result["volumeInfo"]["publishedDate"], '%Y-%m-%d')

        return AudioBookResult(
            result["volumeInfo"]["title"],
            result["volumeInfo"]["authors"][0],
            result["volumeInfo"]["description"],
            result["volumeInfo"]["categories"],
            result["volumeInfo"]["industryIdentifiers"][0]["identifier"],
            result["volumeInfo"]["imageLinks"]["thumbnail"],
            all_authors=result["volumeInfo"]["authors"],
            subtitle=result["volumeInfo"]["subtitle"],
            publisher=result["volumeInfo"]["publisher"],
            publishedDate=dt.year,
            rawData=result
        )

    def get(self, key):
        if key in self._dict:
            return self._dict[key]
        else:
            None

    def __len__(self):
        return 1