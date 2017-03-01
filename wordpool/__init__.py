import random
import codecs
# import unicodedata
import six


class WordList(list):
    """A single list of words.

    :param iterable: If a string type, try to open a file. Otherwise, just call
        the normal list constructor.

    """
    def __init__(self, iterable=None):
        if isinstance(iterable, (six.string_types, six.text_type)):
            with codecs.open(iterable, encoding="utf-8") as f:
                super(WordList, self).__init__(sorted(f.read().split()))
        else:
            super(WordList, self).__init__(iterable)

    def shuffle(self):
        """Shuffle the list in place. Also returns itself to facilitate
        chaining.

        """
        random.shuffle(self)
        return self


class WordPool(object):
    """Handles operations for entire word pools.

    :param str path: Path to word pool.
    :param int num_lists: The number of lists to generate out of the entire
        pool.

    """
    def __init__(self, path, num_lists=25):
        words = WordList(path).shuffle()
        assert len(words) % num_lists == 0
        step = int(len(words) / num_lists)
        self.lists = [WordList(words[step*n:(step*n + step)]) for n in range(num_lists)]
        assert all([len(l) == step for l in self.lists])

    def __str__(self):
        return str(self.lists)

    def __len__(self):
        return len(self.lists)

    def __iter__(self):
        for word_list in self.lists:
            yield word_list

    def __getitem__(self, item):
        return self.lists[item]

    def save(self, dest):
        """Save the word pool as individual list files."""
        raise NotImplementedError
