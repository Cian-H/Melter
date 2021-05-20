#!/usr/bin/env python3
# *_* coding: utf-8 *_*

from MTPy.mtpy import MeltpoolTomography
import inspect


# A class for wrapping generators and adding the ability to increment
# a progress bar
class ProgBar_Wrapper():

    def __init__(self, generator, progress_bar,
                 start=0, end=100, step=1):
        # If the item isnt a generator make it into one
        if not hasattr(generator, "__next__"):
            generator = (x for x in generator)
        self.generator = generator
        self.progress_bar = progress_bar
        self.progress_bar.value = start
        self.progress_bar.max = end
        self.step = step

    def __next__(self):
        output = next(self.generator)
        self.progress_bar.value += self.step
        return output

    def __iter__(self):
        return self


# This class is basically MTPy modified to replace tqdm progress bars with
# Kivy GUI ones
class MT_Modded(MeltpoolTomography):

    # __init__ includes a dict containing progress bars and
    # sets progressbars to be controlled by  a method of the object
    def __init__(self, *args, **kwargs):
        kwargs["progressbar"] = self._progressbar
        self.progress_bars = dict()
        super(MT_Modded, self).__init__(*args, **kwargs)

    # This function is intended to replace tqdm in the mtpy module
    def _progressbar(self, *args, **kwargs):
        # get name of calling function for keeping track
        current_func = inspect.getframeinfo(
                           inspect.currentframe().f_back).function
        # if progbar has an entry
        if current_func in self.progress_bars:
            current_bar = self.progress_bars[current_func]
            # Then, wrap the generator to increment value while iterating
            wrapped_generator = ProgBar_Wrapper(args[0], current_bar,
                                                start=0, end=kwargs["total"])
            return wrapped_generator
        else:
            return args[0]  # if not top-level, return unmodified generator
