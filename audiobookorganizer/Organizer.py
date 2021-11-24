import os
import sys

from audiobookorganizer.core.Tagger import FileMetadata
from audiobookorganizer.core.Utils import has_subfolders, get_filetype, get_folders_from_path, get_first_audio_file
from audiobookorganizer.metadata.GoogleBooks import Provider as GoogleBooksProvider
import cli_ui as ui


class App:
    _VERSION = "0.0.1 alpha"

    _MENU_ITEM_CHECK_TAGS = "Check for missing Tags"
    _MENU_ITEM_EXIT = "Exit"

    def __init__(self, source="", destination=None):
        self.metadataprovider = GoogleBooksProvider()
        pass

    def main_menu(self):
        tasks = [
            App._MENU_ITEM_CHECK_TAGS,
            App._MENU_ITEM_EXIT
        ]
        choice = ui.ask_choice("Choose a task", choices=tasks)

        if choice is None:
            ui.error("Please select a task")
            self.main_menu()
        elif choice == App._MENU_ITEM_CHECK_TAGS:
            self.check_tags()
        elif choice == App._MENU_ITEM_EXIT:
            print(choice)

    def check_tags(self):
        path = ui.ask_string("Enter path to your audiobooks")
        if path is None:
            path = "\\\\10.1.1.210\\media\\audio\\audio_books"
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

                for file in f_names:
                    print(root, file)
                    # print(filetype(file))
                # tagread(os.path.join(root))
                # print(root, d_names, f_names)

    def run(self):
        ui.setup(color="always")
        ui.info("Welcome to", ui.bold, ui.red, "AudioBookOrganizer v" + App._VERSION)
        self.main_menu()
