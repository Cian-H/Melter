class CalCurve():

    def __init__(self):
        self.name = "None"
        self.formula = "y=x"
        self.response = ""
        self.units = ""

    def __call__(self, x):
        return x

    def __str__(self):
        return self.name


class AlSi7Mg(CalCurve):

    def __init__(self):
        self.name = "AlSi7Mg"
        self.formula = "N/A"
        self.response = "Temperature"
        self.units = "°C"

    def __call__(self, x):
        return x


class Al6061(CalCurve):

    def __init__(self):
        self.name = "Al6061"
        self.formula = "T=(V+84.66)/1.45"
        self.response = "Temperature"
        self.units = "°C"

    def __call__(self, x):
        return (x + 84.661) / 1.4516


class SS15_5PH(CalCurve):

    def __init__(self):
        self.name = "15-5PH Stainless Steel"
        self.formula = "N/A"
        self.response = "Temperature"
        self.units = "°C"

    def __call__(self, x):
        return x


class H13(CalCurve):

    def __init__(self):
        self.name = "H13 Tool Steel"
        self.formula = "N/A"
        self.response = "Temperature"
        self.units = "°C"

    def __call__(self, x):
        return x


class Inconel625(CalCurve):

    def __init__(self):
        self.name = "Inconel 625"
        self.formula = "N/A"
        self.response = "Temperature"
        self.units = "°C"

    def __call__(self, x):
        return x


class Inconel718(CalCurve):

    def __init__(self):
        self.name = "Inconel 718"
        self.formula = "N/A"
        self.response = "Temperature"
        self.units = "°C"

    def __call__(self, x):
        return x


class Custom(CalCurve):

    def __init__(self):
        self.name = "Custom"
        self.formula = "y=mx+c"
        self.response = "Response"
        self.units = "U"

    def __call__(self, x):
        return x
