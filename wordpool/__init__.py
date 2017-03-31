import random
import numpy as np
import pandas as pd
from pkg_resources import resource_filename

__version__ = "0.2.dev"


def load(filename, from_data_package=True):
    """Return contents of a word list.

    :param str filename:
    :param bool from_data_package: When True (the default), load data from the
        ``wordpool.data`` package. Otherwise, treat the filename as an absolute
        path to load arbitrary wordpools from.
    :rtype: pd.DataFrame

    """
    if from_data_package:
        src = resource_filename("wordpool.data", filename)
    else:
        src = filename
    return pd.read_table(src)


def assign_list_numbers(df, n_lists):
    """Assign or reassign list numbers to all words in the pool.

    :param pd.DataFrame df: Input word pool
    :param int n_lists: Total number of lists.
    :returns: Word pool with list numbers assigned

    """
    assert len(df) % n_lists == 0
    words_per_list = int(len(df) / n_lists)
    listnos = np.array(
        [[n]*words_per_list for n in range(n_lists)]).flatten()
    df["listno"] = listnos
    return df


def shuffle_words(df):
    """Shuffle words.

    :param pd.DataFrame df: Input word pool
    :returns: Shuffled pool

    """
    shuffled = df.reindex(np.random.permutation(df.index))
    return shuffled.reset_index(drop=True)


def shuffle_within_lists(df):
    """Shuffle within lists in the pool (i.e., shuffle each list but do not
    move any words between lists. This requires that list
    numbers have alreay been assigned.

    :param pd.DataFrame df: Input word pool
    :returns: Pool with lists shuffled

    """
    if "listno" not in df.columns:
        raise RuntimeError("You must assign list numbers first.")

    shuffled = []
    for listno in df.listno.unique():
        list_ = df[df.listno == listno]
        shuffled.append(list_.reindex(np.random.permutation(list_.index)))

    return pd.concat(shuffled).reset_index(drop=True)
