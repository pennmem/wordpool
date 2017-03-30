import random
import numpy as np
import pandas as pd
from pkg_resources import resource_string

__version__ = "0.2.dev"


def load(filename):
    """Return contents of a word list contained in the wordpool.data
    package.

    :param str filename:
    :rtype: pd.DataFrame

    """
    words = resource_string("wordpool.data", filename).decode("utf-8")
    return pd.read_table(words)


class WordPool(object):
    """Utilities for working with word pools.

    :param str filename: Filename containing the word pool. The word pool must
        be in a format readable with `pd.read_table` and contain a header row
        to name the columns; a ``word`` column is required to label the words
        in the pool.
    :param int n_lists: Number of lists to be made from the word pool.

    """
    def __init__(self, filename, n_lists=None):
        self.df = pd.read_table(filename)
        assert "word" in self.df.columns

        if n_lists is not None:
            self.assign_list_numbers(n_lists)

    def __str__(self):
        return str(self.df)

    def __len__(self):
        return len(self.df)

    def __iter__(self):
        for idx, row in self.df.iterrows():
            yield row

    def prepend(self, words):
        """Insert words at the beginning of the word pool.

        :param iterable words:
        :returns: self

        """
        self.df = pd.concat([words, self.df])
        return self

    def append(self, words):
        """Append words to the end of the word pool.

        :param iterable words:
        :returns: self

        """
        self.df = pd.concat([self.df, words])
        return self

    def assign_list_numbers(self, n_lists):
        """Assign or reassign list numbers to all words in the pool.

        :param int n_lists: Total number of lists.

        """
        assert len(self.df) % n_lists == 0
        words_per_list = int(len(self.df) / n_lists)
        listnos = np.array(
            [[n]*words_per_list for n in range(n_lists)]).flatten()
        self.df["listno"] = listnos

    def shuffle_words(self, frozen=[]):
        """Shuffle words in place.

        :param list frozen: List of word numbers to exclude from shuffling.
        :returns: self

        """
        frozen_words = self.df[self.df.index.isin(frozen)]
        shuffle_words = self.df[~self.df.index.isin(frozen)]
        shuffled = shuffle_words.reindex(np.random.permutation(shuffle_words.index))
        self.df = pd.concat([frozen_words, shuffled]).reset_index(drop=True)
        return self

    def shuffle_within_lists(self, frozen=[]):
        """Shuffle within lists in the pool (i.e., shuffle each list but do not
        move any words between lists. This requires that list
        numbers have alreay been assigned.

        :param list frozen: List numbers to not shuffle.

        """
        frozen_lists = self.df[self.df.listno.isin(frozen)]
        shuffle_lists = self.df[~self.df.listno.isin(frozen)]

        shuffled_lists = []
        for listno in shuffle_lists.listno.unique():
            list_ = shuffle_lists[shuffle_lists.listno == listno]
            list_.apply(lambda col: sorted(col, key=lambda _: random.random()))
            shuffled_lists.append(list_)

        self.df = pd.concat([frozen_lists, shuffle_lists])
        return self

    def to_dict(self):
        """Converts the word pool to a dict representation. Format::

            {
                "lists": [<list of lists>]
            }

        See :meth:`WordList.to_dict` for details.

        """
        return {
            "lists": [words.to_dict() for words in self.lists]
        }


if __name__ == "__main__":
    import os.path as osp
    pool = WordPool(osp.join(osp.dirname(__file__), "data", "ram_wordpool_en.txt"))
    pool.shuffle_words()
    print(pool.head())
    pool.assign_list_numbers(25)
    pool.shuffle_within_lists()
    print(pool.head())
