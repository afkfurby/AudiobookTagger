import os
import sys

import music_tag

from pathlib import Path

from audiobookorganizer.core.Helpers import MetadataDict
from audiobookorganizer.core.Tagger import FileMetadata
from audiobookorganizer.core.Utils import has_subfolders, get_filetype, get_folders_from_path, get_first_audio_file
from audiobookorganizer.metadata.GoogleBooks import Provider as GoogleBooksProvider
import cli_ui as ui


class App:
    _VERSION = "0.0.1 alpha"

    _MENU_ITEM_CHECK_TAGS = "Check for missing Tags"
    _MENU_ITEM_ORGANIZE = "Organize Audiobooks ins Folders"
    _MENU_ITEM_EXIT = "Exit"

    def __init__(self, source="", destination=None):
        self.metadataprovider = GoogleBooksProvider()
        pass

    def main_menu(self):
        tasks = [
            App._MENU_ITEM_CHECK_TAGS,
            App._MENU_ITEM_ORGANIZE,
            App._MENU_ITEM_EXIT
        ]
        choice = ui.ask_choice("Choose a task [" + App._MENU_ITEM_ORGANIZE + "]", choices=tasks)

        if choice is None:
            # ui.error("Please select a task")
            # self.main_menu()
            choice = App._MENU_ITEM_ORGANIZE

        if choice == App._MENU_ITEM_CHECK_TAGS:
            self.check_tags()
        elif choice == App._MENU_ITEM_ORGANIZE:
            self.organize()
        elif choice == App._MENU_ITEM_EXIT:
            print(choice)

    def check_tags(self):
        path = ui.ask_string("Enter path to your audiobooks")
        if path is None:
            path = "\\\\10.1.1.210\\media\\audio\\audio_books"
            path = "C:\\Users\\Vital\\OpenAudible\\books"
        ui.info("Checking tags in", ui.bold, path)

        for root, d_names, f_names in os.walk(path):
            if not has_subfolders(root):

                folder = root.replace(path + "\\", "")
                folders = get_folders_from_path(folder)

                path_author, path_series, path_title = None, None, None

                if len(folders) == 2:  # author, title
                    path_author = folders[0]
                    path_title = folders[1]
                elif len(folders) == 3:  # author, series, title
                    path_author = folders[0]
                    path_series = folders[1]
                    path_title = folders[2]
                elif len(folders) == 1:  # should be title fo book
                    path_title = folders[0]
                    ui.info("Only detected book title from path", ui.bold, path_title)
                else:
                    ui.error("Folder structure of", folder, "not ok skipping")
                    ui.info("TODO: implement user handling")
                    # TODO: implement user handling of corrupted folder structure
                    continue

                ui.info(ui.green, "Found Book:", ui.reset, ui.bold, "Title:", ui.reset, path_title, ui.reset, ui.bold,
                        "Author:", path_author, ui.reset, ui.bold, "Series:", path_series, ui.reset)

                file = get_first_audio_file(root, f_names)
                metadata = FileMetadata(os.path.join(root, file))

                # ui.info(ui.green, "Metadata (Path/File):", ui.reset,
                #         ui.bold, "Title:", ui.reset, path_title, "/", metadata.get("title"),
                #         ui.bold, "Author:", ui.reset, path_author, "/", metadata.get("author"),
                #         ui.bold, "Series:", ui.reset, path_series, "/", metadata.get("series"),
                #         )

                results = self.metadataprovider.search(author=metadata.get("author"), title=metadata.get("title"), getfirst=True)

                if len(results) > 0:
                    pass

                headers = ["Tag", "File", "New"]
                data = []
                for key, value in FileMetadata.TAGMAP.items():
                    fval = str(metadata.get(key))
                    fval = None if str(fval) == "" else fval

                    # new_color = ui.green if fval != str(results.get(key)) else ui.red if results.get(
                    #     key) is None else ui.reset,

                    # fval = str(fval)[:40] + '..' if len(str(fval)) > 40 else fval

                    new = results.get(key)

                    data.append((
                        (ui.bold, key),
                        (
                            ui.red if fval is None else ui.reset,
                            str(fval)[:40] + '..' if len(str(fval)) > 40 else fval
                        ),
                        (
                            # ui.green if fval != str(results.get(key)) else ui.red if results.get(key) is None else ui.reset,
                            ui.red if results.get(key) is None else ui.green if fval != str(results.get(key)) else ui.reset,

                            # ui.red if results.get(key) is None else ui.green,
                            str(results.get(key))[:40] + '..' if len(str(results.get(key))) > 40 else results.get(key)
                        )))

                # data = [
                #     [(ui.bold, "John"), (green, 10.0), None],
                #     [(bold, "Jane"), (green, 5.0)],
                # ]

                ui.info_table(data, headers=headers)

                for item in FileMetadata.UPDATABLE_TAGS:
                    metadata.update(item, results.get(item))

                metadict = metadata.new_metadata

                for file in f_names:
                    # print(root, file)
                    # print(filetype(file))
                    if get_filetype(os.path.join(root, file))[0] == "audio":
                        metaobj = FileMetadata(os.path.join(root, file))
                        metaobj.new_metadata = metadict
                        metaobj.save()
                # tagread(os.path.join(root))
                # print(root, d_names, f_names)

    # def _update_metatags(self):
    #     file = get_first_audio_file(root, f_names)
    #     file = music_tag.load_file(file)
    #     metadata = FileMetadata(os.path.join(root, file))

    def _walk_path(self, path):
        for root, d_names, f_names in os.walk(path):
            if not has_subfolders(root):  # no more subfolders, here should be audio files
                if root == path:
                    # no folders, just files
                    for file in f_names:
                        filemeta = MetadataDict.from_file(os.path.join(root, file))
                        gbmeta = MetadataDict.from_googlebooks(filemeta.Author, filemeta.Title)
                        # print(filemeta)
                        # print(gbmeta)
                        filemeta.update(gbmeta)
                        print(filemeta)

                        # print(f'filemeta has changed? { filemeta.has_changed()}')
                        filemeta.save_to_file()
                        self._generate_folder_structure(root, file, filemeta)

                else:  # folder structure
                    folders = self._get_folders_from_path(root, path)

                    print(folders)

    def _generate_folder_structure(self, path, file, metadata, save_cover=True, move=True):  # if move=False, file will be copied

        if metadata.Series is None:
            fullpath = os.path.join(path, metadata.Author, metadata.Title)
        else:
            fullpath = os.path.join(path, metadata.Author, metadata.Series, metadata.Title)

        Path(fullpath).mkdir(parents=True, exist_ok=True)

        if save_cover:
            metadata.export_cover(fullpath, case_sensitive=True)  # save cover file

        if move:
            os.rename(os.path.join(path, file), os.path.join(fullpath, file))
        else:
            import shutil
            shutil.copy2(os.path.join(path, file), os.path.join(fullpath, file))

    def _iterate_files(self, files, callback):
        for file in files:
            pass

    def _get_folders_from_path(self, root, path):
        folder = root.replace(path + "\\", "")
        return get_folders_from_path(folder)

    def organize(self):
        default_path = "\\\\10.1.1.210\\media\\audio\\audio_books"
        default_path = "C:\\Users\\Vital\\OpenAudible\\books"
        default_path = "C:\\PyCharmProjects\\googlebooks\\data"
        path = ui.ask_string("Enter path to your audiobooks", default=default_path)
        ui.info("Checking tags in", ui.bold, path)
        self._walk_path(path)

    def run(self):
        ui.setup(color="always")
        ui.info("Welcome to", ui.bold, ui.red, "AudioBookOrganizer v" + App._VERSION)
        self.main_menu()
