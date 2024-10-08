import operator as _op


class __Base():

    def __init__(self):
        self.name = "None"

    def __str__(self):
        return self.name


class Greater(__Base):

    def __init__(self):
        self.name = ">"

    def __call__(self, *args):
        return _op.gt(*args)


class GreaterOrEqual(__Base):

    def __init__(self):
        self.name = "≥"

    def __call__(self, *args):
        return _op.ge(*args)


class Equal(__Base):

    def __init__(self):
        self.name = "="

    def __call__(self, *args):
        return _op.eq(*args)


class NotEqual(__Base):

    def __init__(self):
        self.name = "≠"

    def __call__(self, *args):
        return _op.ne(*args)


class LessOrEqual(__Base):

    def __init__(self):
        self.name = "≤"

    def __call__(self, *args):
        return _op.le(*args)


class Less(__Base):

    def __init__(self):
        self.name = "<"

    def __call__(self, *args):
        return _op.lt(*args)
