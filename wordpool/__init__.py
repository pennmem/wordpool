import time
import random
import codecs
import six

try:
    import pandas as pd
except ImportError:
    pd = None

__version__ = "0.2.dev"


class WordList(list):
    """A single list of words.

    :param iterable: If a string type, try to open a file. Otherwise, just call
        the normal list constructor.
    :param dict metadata: A dict of metadata to associate with the list. If no
        ``created`` key is given, one will be added which provides a timestamp
        in seconds since the epoch.

    """
    def __init__(self, iterable=None, metadata=None):
        if isinstance(iterable, (six.string_types, six.text_type)):
            with codecs.open(iterable, encoding="utf-8") as f:
                super(WordList, self).__init__(sorted(f.read().split()))
        else:
            super(WordList, self).__init__(iterable)

        self.metadata = metadata or {}
        if "created" not in self.metadata:
            self.metadata["created"] = time.time()

    def shuffle(self):
        """Shuffle the list in place. Also returns itself to facilitate
        chaining.

        """
        random.shuffle(self)
        return self

    def choose(self, n):
        """Randomly select n words from the list.

        :param int n: Number of words to select.
        :returns: new :class:`WordList` instance.

        """
        assert 0 < n <= len(self)
        words = random.sample(self, n)
        return WordList(words)

    def to_dict(self):
        """Convert to a dict of the form::

            {
                "metadata": self.metadata,
                "words": [<list of words in self>]
            }

        """
        return {
            "metadata": self.metadata,
            "words": [word for word in self]
        }

    def to_dataframe(self):
        """Convert to a :class:`DataFrame`. Metadata will be repeated for each
        word in the list.

        """
        if pd is None:
            raise RuntimeError("You must install pandas to convert to a DataFrame!")
        words = [word for word in self]
        d = {
            key: [value]*len(words) for key, value in self.metadata.items()
        }
        d.update({"word": words})
        return pd.DataFrame(d)

    def to_text(self, filename, delimiter="\n"):
        """Save the list of words only to a plaintext file.

        :param str filename:
        :param str delimiter:

        """
        with open(filename, "w") as outfile:
            outfile.write(delimiter.join(self))


class WordPool(object):
    """Handles operations for entire word pools. Here, a word pool is
    considered to be made up of a series one or more word lists.

    .. note:: Word lists must contain the same number of words!

    :param list lists: Word lists to include (coerced to :class:`WordList` if
       not already).
    :raises: AssertionError when lists are not all the same length.

    """
    def __init__(self, lists):
        self.lists = [WordList(list_) if not isinstance(list_, WordList) else list_
                      for list_ in lists]
        length = len(self.lists[0])
        for list_ in self.lists:
            assert length == len(list_)

    def __str__(self):
        return str(self.lists)

    def __len__(self):
        return len(self.lists)

    def __iter__(self):
        for word_list in self.lists:
            yield word_list

    def __getitem__(self, item):
        return self.lists[item]

    def shuffle_lists(self, frozen=[]):
        """Shuffle within lists in the pool (i.e., shuffle each list but do not
        move any words between lists. Returns self.

        :param list frozen: Indices of lists to not shuffle.

        """
        for n, list_ in enumerate(self.lists):
            if n in frozen:
                continue
            list_.shuffle()
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

    def to_dataframe(self, add_listno=True):
        """Convert the pool to a :class:`pd.DataFrame`.

        :param bool add_listno: When True, include a `listno` column to keep
            track of which list number a given word is from.

        """
        if pd is None:
            raise RutimeError("Please install Pandas")

        dfs = []
        for listno, list_ in enumerate(self.lists):
            df = list_.to_dataframe()
            if add_listno:
                df["listno"] = [listno]*len(list_)
            dfs.append(df)

        return pd.concat(dfs)
