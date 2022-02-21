#!/usr/bin/env python3
# *_* coding: utf-8 *_*

# Kivy module imports
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown


class DropdownButton(Button):

    def __init__(self,
                 option_list=None,
                 default_selection=None,
                 bound_textfields={},
                 **kwargs):
        # ensure "test" kwarg isnt present
        if "test" in kwargs:
            kwargs.pop("test")

        # Add default args if they're not specifically assigned
        self.defaultkwargs = \
            {"background_color": [x * 0.75 for x in self.background_color],
             }

        for keyword, arg in self.defaultkwargs.items():
            if keyword not in kwargs:
                kwargs[keyword] = arg

        # self.bound_textfields is a dict of objects as keys,
        # values are either the name of textfield to update or tuple containing
        # the textfield name AND a function that maps the selection to a new string
        self.bound_textfields = bound_textfields
        self.kwargs = kwargs
        super(DropdownButton, self).__init__(**self.kwargs)

        if option_list is not None:
            self.populate_dropdown(option_list)

        if type(default_selection) == str:
            self.current_selection = self.objects_dict[default_selection]
        else:
            self.current_selection = default_selection

    # Populates dropdown with contents of list given
    def populate_dropdown(self, option_list):
        kwargs = self.kwargs.copy()
        kwargs["size_hint_y"] = None
        if "height" not in kwargs:
            kwargs["height"] = 50
        if "__no_builder" in kwargs:
            kwargs.pop("__no_builder")

        self.dropdown_list = None
        self.dropdown_list = DropDown()

        self.objects_dict = {str(x): x for x in option_list}

        for x in self.objects_dict.keys():
            button = Button(text=x, **kwargs)
            button.bind(on_release=self._bind_button)
            self.dropdown_list.add_widget(button)

        self.bind(on_release=self.dropdown_list.open)
        self.dropdown_list.bind(on_select=self._select_item)

    # Function to bind button to dropdown
    def _bind_button(self, btn):
        self.dropdown_list.select(btn.text)

    def _update_label(self, instance, x):
        setattr(self, "text", x)

    # This function runs whenever an item from the dropdown is selected
    def _select_item(self, instance, selection):
        self.current_selection = self.objects_dict[selection]
        self._update_label(instance, selection)
        self.update_bound_textfields(selection)

    def update_bound_textfields(self, text):
        for object, field in self.bound_textfields.items():
            if type(field) == str:
                setattr(object, field, text)
            elif type(field) == tuple:
                setattr(object, field[0], field[1](text))
