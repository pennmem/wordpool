from pkg_resources import resource_string
import pandas as pd


def read_list(filename):
    """Return contents of a word list contained in the wordpool.data
    package.

    :param str filename:
    :rtype: pd.DataFrame

    """
    words = resource_string("wordpool.data", filename).decode("utf-8")
    return pd.read_table(words)
