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


def shuffle_words(df, frozen=[]):
    """Shuffle words in place.

    :param pd.DataFrame df: Input word pool
    :param list frozen: List of word numbers to exclude from shuffling.
    :returns: Shuffled pool

    """
    frozen_words = df[df.index.isin(frozen)]
    shuffle_words = df[~df.index.isin(frozen)]
    shuffled = shuffle_words.reindex(np.random.permutation(shuffle_words.index))
    return pd.concat([frozen_words, shuffled]).reset_index(drop=True)


def shuffle_within_lists(df, frozen=[]):
    """Shuffle within lists in the pool (i.e., shuffle each list but do not
    move any words between lists. This requires that list
    numbers have alreay been assigned.

    :param pd.DataFrame df: Input word pool
    :param list frozen: List numbers to not shuffle.
    :returns: Pool with lists shuffled

    """
    frozen_lists = df[df.listno.isin(frozen)]
    shuffle_lists = df[~df.listno.isin(frozen)]

    shuffled_lists = []
    for listno in shuffle_lists.listno.unique():
        list_ = shuffle_lists[shuffle_lists.listno == listno]
        list_.apply(lambda col: sorted(col, key=lambda _: random.random()))
        shuffled_lists.append(list_)

    return pd.concat([frozen_lists, shuffle_lists])
