#!/usr/bin/env python3
# *_* coding: utf-8 *_*

from kivy.app import App
# For polymorphism (e.g. phone app) use conditional import below
# The code below currently is kind of pointless and "Main_Phone" does not exist
# but it demonstrates the plan for polymorphism
mode = "desktop"
if mode == "desktop":
    from Main.Main_Desktop import Main
elif mode == "phone":
    from Main.Main_Phone import Main


# Create application class
class Melter(App):

    def build(self):
        return Main()


dev_mode = False


if (__name__ == "__main__") and dev_mode:
    # DEBUG
    test = Melter()
    test.run()
    breakpoint()
elif __name__ == "__main__":
    Melter().run()
