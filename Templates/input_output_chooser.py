#!/usr/bin/env python3
# *_* coding: utf-8 *_*

# Kivy module imports
from kivy.lang.builder import Builder
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
# Other python module imports
from types import SimpleNamespace

Builder.load_file("Templates/file_chooser_popup.kv")


# Create classes for loaded kv files
# This class contains the popup for choosing files
class FileChooserPopup(Popup):
    load = ObjectProperty()


class InputOutputChooser(BoxLayout):
    load = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super(InputOutputChooser, self).__init__(*args, **kwargs)
        starting_cache = {"popups": {},  # A dict to contain all popup objects
                          "shared_io_choosers": False,
                          "parent_app": False}
        self.cache = SimpleNamespace(**starting_cache)

    # The functions "open" and "load" are used to load the file chooser popup
    def open_chooser(self, pathattr: str):
        # Wrapper function to allow for multiple different choosers
        def load_chooser_wrapper(selection):
            return self.load_chooser(pathattr, selection)

        self.cache.popups[pathattr] = \
            FileChooserPopup(load=load_chooser_wrapper)
        self.cache.popups[pathattr].open()

    def load_chooser(self, pathattr: str, selection):
        path_string = str(selection[0])
        setattr(self, pathattr, path_string)
        self.cache.popups[pathattr].dismiss()

        # check for non-empty list i.e. file selected
        if pathattr in self.__dict__:
            # set own details based on selection
            id = getattr(self.ids, pathattr)
            id.text = getattr(self, pathattr)
            # set parameters for shared and parent if present
            if self.cache.shared_io_choosers:
                for chooser in self.cache.shared_io_choosers:
                    id = getattr(chooser.ids, pathattr)
                    id.text = getattr(self, pathattr)
            if self.cache.parent_app:
                setattr(self.cache.parent_app.cache, pathattr, path_string)
