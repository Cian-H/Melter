#!/usr/bin/env python3
# *_* coding: utf-8 *_*

from kivy.app import App
# For polymorphism (e.g. phone app) use conditional import below
# The code below currently is kind of pointless and "Main_Phone" does not exist
# but it demonstrates the plan for polymorphism
mode = "desktop"
if mode == "desktop":
    from Main.Main_Desktop import Main
# elif mode == "phone":
#     from Main.Main_Phone import Main


# Create application class
class Melter(App):

    def build(self):
        return Main()


def main():
    Melter().run()


def main_debug():
    test = Melter()
    test.run()
    breakpoint()


if __name__ == "__main__":
    dev_mode = False

    if not dev_mode:
        main()
    else:
        main_debug()
