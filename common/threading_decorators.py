#!/usr/bin/env python3
# *_* coding: utf-8 *_*

from threading import Thread
from functools import wraps


# Wrapper for running a function in a parallel thread
def run_in_thread(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
    return wrapper
