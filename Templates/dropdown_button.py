#!/usr/bin/env python3
# *_* coding: utf-8 *_*

# Kivy module imports
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown


class DropdownButton(Button):
    def __init__(self, option_list=None, **kwargs):
        # ensure "text" kwarg isnt present
        if "test" in kwargs:
            kwargs.pop("test")

        # Add default args if they're not specifically assigned
        self.defaultkwargs = \
            {"background_color": [x*0.75 for x in self.background_color],
             }

        for keyword, arg in self.defaultkwargs.items():
            if keyword not in kwargs:
                kwargs[keyword] = arg

        self.kwargs = kwargs
        super(DropdownButton, self).__init__(**self.kwargs)

        # Create lambdas for callbacks
        self.__bind_button = lambda btn: self.dropdown_list.select(btn.text)
        self.__update_label = lambda instance, x: setattr(self, "text", x)

        if option_list is not None:
            self.populate_dropdown(option_list)

    def populate_dropdown(self, option_list):
        kwargs = self.kwargs.copy()
        kwargs["size_hint_y"] = None
        if "height" not in kwargs:
            kwargs["height"] = 50
        if "__no_builder" in kwargs:
            kwargs.pop("__no_builder")

        self.dropdown_list = None
        self.dropdown_list = DropDown()

        for x in option_list:
            button = Button(text=x, **kwargs)
            # button = Button(text=x, size_hint_y=None, height=50)
            button.bind(on_release=self.__bind_button)
            self.dropdown_list.add_widget(button)

        self.bind(on_release=self.dropdown_list.open)
        self.dropdown_list.bind(on_select=self.__update_label)
