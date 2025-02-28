import os
import sys
import types
import importlib

from rich.console import Console
from rich.markdown import Markdown

from .Errors import NotHereError, NotAnEgo


class Talk:
    """Class that allows you to talk to the personas.

    :param persona: The name of the persona you want to talk too file must be in current directory.
    :type persona: str
    """

    def __init__(self, persona: str = ""):
        try:
            mod = types.ModuleType(persona)
            with open(persona, "r") as fh:
                data = fh.read()
            exec(data, mod.__dict__)
            getattr(mod, persona)()
        except NotAnEgo:
            console = Console()
            console.print(Markdown(f"> But {persona} isn't sentient!"))
        except Exception as e:
            print(e)
            console = Console()
            block = f"> You try to talk to {persona}, but they're not here!"
            console.print(Markdown(block))


def cmd():
    sys.path.append(os.path.expanduser(os.getcwd()))
    Talk(sys.argv[1])
