

def test_series_fetcher():
    from audiobookorganizer.core.Utils import get_series_from_googlebooks
    get_series_from_googlebooks()


# test_series_fetcher()


def mutagen_test():
    file = "\\\\10.1.1.210\\media\\audio\\audio_books\\Adrian Tchaikovsky\\Die Kinder der Zeit\\Adrian Tchaikovsky - Die Kinder der Zeit (1).mp3"
    import mutagen
    mutagen.File(file)

    from mutagen.id3 import ID3, TXXX