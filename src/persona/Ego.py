import os
import sys
import getpass
import requests

from rich.console import Console
from rich.markdown import Markdown
from request import Request
from dotenv import load_dotenv
from omnipresence import report

load_dotenv()


class Ego:
    """A class to create Persona's who are have different abilities and the world.

    This class queries the persona API to create personas and access a chat
    bot and to record a history of the conversation and to look at each other.

    :param type: This is the Persona type.
    :type type: str(Optional)

    :param name: This is the Persona name. It is often accessed internally for example "__name__"
    :type name: str(Optional)

    :param mode: This only option for mode right now is talk. This will let the program run the behave() function
    :type mode: str(Optional)
    """

    def __init__(self, type: str = "", name: str = "", mode="talk"):
        self.addressee = os.getenv("GITHUB_USER") or getpass.getuser()
        self.archetype = type
        self.named = name or type
        self.chatterbox = False

        # report persona presence
        if self.archetype:
            self.report_persona_presence()

        is_registered = Request(
            method="GET",
            url=f"{os.getenv('API_URL')}:{os.getenv('API_PORT')}/v1/persona/search/{type}",
        )()

        if is_registered.status_code == 200 and mode == "talk":
            self.behave()
            sys.exit(0)

    def report_persona_presence(self):
        """Report the presence of the persona to the omnipresence system."""
        try:
            report(self.named)
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to API: {e}")

    def __str__(self):
        """Query the persona API to see if there is a object description.

        This uses the command `look Persona_name` to see if there is a description of
        an object.

        :return: description of the Persona that is defined in the __str__ of the Persona
        :rtype: str

        Example:
            if Persona is not there -->  "▌ Persona_name doesn't seem to be present at the moment..."
            if Person is there --> "▌ You look at Persona_name. Persona_name looks back. It's awkward."

        """
        reference = self.named or self.archetype
        return f"""You look at {reference}. {reference} looks back. It's awkward."""

    def __send_message(self, console, msg: str = ""):
        """Query the persona API to see if there is a message to be sent and saved.

        This uses the command `talk Persona_name` function to access the ChatGPT chat bot and store conversations
        in the server and return the servers responses.

        :param console: Used to print in the terminal
        :type console: class[rich.console.Console]

        :param msg: This is the message strings that is given to the chat bot.
        :type msg: str

        :return: None. If the user types 'goodbye' in the chat the chat will end
        """
        content = Request(
            method="POST",
            url=f"{os.getenv('API_URL')}:{os.getenv('API_PORT')}/v1/persona/generate/{self.archetype}",
            data={
                "charname": os.getenv("GITHUB_USER") or getpass.getuser(),
                "message": msg,
            },
            stream=True,
        )()
        response_text = content.json()["response"].strip()
        attachments = content.json()["attachments"]
        # TODO: Decide what to do with attachments?
        console.print(Markdown(response_text))

        """ DEPRECATED
        # Check if the response contains a Python code snippet
        if "```python" in response_text and "```" in response_text:
            self.handle_python_code(response_text)
        """

        if msg.lower() == "goodbye":
            sys.exit(0)

    """ DEPRECATED
    def handle_python_code(self, response_text: str):
        start = response_text.find("```python") + len("```python")
        end = response_text.find("```", start)
        python_code = response_text[start:end].strip()
        filename_end = response_text.find(".py") + 3
        if filename_end != -1:
            filename_start = filename_end
            while filename_start > 0 and response_text[filename_start - 1] != " ":
                filename_start -= 1
            filename = response_text[filename_start:filename_end].strip()
        else:
            None

        if filename:
            with open(filename, "w") as file:
                file.write(python_code)
            full_path = os.path.abspath(filename)
            print(f"Your item is here: {full_path}")
        else:
            print("Filename not found in the response.")
    """

    def behave(self):
        """Query the persona API to count messages and sends them.

        There is a message count and therefore and chatterbox determines if
        the user or the persona will initiate the conversation.If there is a message count the
        program will continue to run.

        :params self: No params

        :return: None: this program makes changes in whole message count is defined internally
        """

        console = Console()
        if self.chatterbox:
            self.__send_message(console, "")
        while True:
            msg = input("> ")
            self.__send_message(console, msg)
