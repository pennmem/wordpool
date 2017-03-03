import json
from pkg_resources import resource_string


def read_list(filename):
    """Return contents of a word list contained in the wordpool.data
    package.

    :param str filename:
    :returns: list of words

    """
    words = resource_string("wordpool.data", filename).decode()
    if filename.endswith(".json"):
        return json.loads(words)["words"]
    else:
        return words.split()
