from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty
from kivy.uix.textinput import TextInput
from io import StringIO


# This variation of StringIO communicates back to parent observer
class ObservableStringIO(StringIO):

    def __init__(self, *args, **kwargs):
        if "observer" in kwargs:
            self.observer = kwargs.pop("observer")
        super(ObservableStringIO, self).__init__(*args, **kwargs)

    def write(self, *args, **kwargs):
        # Just need to flip trigger on write. Specific value doesnt matter
        self.observer.trigger = not self.observer.trigger
        super(ObservableStringIO, self).write(*args, **kwargs)


# This StringIO wrapper object outputs string from io to target on every write
class StringIO_toString_Observer(EventDispatcher):
    trigger = BooleanProperty()

    def __init__(self, target, **kwargs):
        self.io_buffer = ObservableStringIO(observer=self)
        self.trigger = False  # <- val doesnt matter as long a bool
        self.target = target
        self.target.text = str(self.io_buffer.getvalue())
        super(StringIO_toString_Observer, self).__init__(**kwargs)

    def on_trigger(self, instance, value):
        self.target.text = str(self.io_buffer.getvalue())


# This console output widget can output io streams if redirected to its
# io_buffer property
class ConsoleOutput(TextInput):
    def __init__(self, *args, **kwargs):
        # Define and apply default kwargs
        defaultkwargs = {"readonly": True,
                         "background_color": (0, 0, 0, 1),
                         "foreground_color": (1, 1, 1, 1)}
        kwargs = {k: (v if k not in kwargs else kwargs[k])
                  for k, v in defaultkwargs.items()}
        # Then call super
        super(ConsoleOutput, self).__init__(*args, **kwargs)
        # Then add observer and ref to io_buffer for ease-of-use
        self.observer = StringIO_toString_Observer(self)
        self.io_buffer = self.observer.io_buffer
