from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Context:

    last_app: Optional[str] = None

    last_website: Optional[str] = None

    last_file: Optional[str] = None

    last_folder: Optional[str] = None

    last_window: Optional[str] = None

    last_search: Optional[str] = None

    last_song: Optional[str] = None

    last_person: Optional[str] = None

    last_action: Optional[str] = None

    variables: dict = field(default_factory=dict)


context = Context()


def remember_app(name):

    context.last_app = name


def remember_website(name):

    context.last_website = name


def remember_file(name):

    context.last_file = name


def remember_folder(name):

    context.last_folder = name


def remember_window(name):

    context.last_window = name


def remember_search(query):

    context.last_search = query


def remember_person(name):

    context.last_person = name


def remember_song(song):

    context.last_song = song


def remember_action(action):

    context.last_action = action


def set_variable(key, value):

    context.variables[key] = value


def get_variable(key):

    return context.variables.get(key)


def clear():

    context.last_app = None
    context.last_website = None
    context.last_file = None
    context.last_folder = None
    context.last_window = None
    context.last_search = None
    context.last_song = None
    context.last_person = None
    context.last_action = None
    context.variables.clear()