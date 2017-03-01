import time
import json
import random
import codecs
# import unicodedata
import six


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

    def save(self, filename, **json_kwargs):
        """Save the list to a plaintext or JSON file. If saving as JSON, the
        resulting file will be of the form produced by
        :meth:`WordList.to_dict`. Saving to plaintext will just save the words.

        :param str filename: Output filename. File type will be determined by
            the suffix (``.txt`` or ``.lst`` for plaintext, ``.json`` for JSON).
        :param dict json_kwargs: Keyword arguments to pass to
            :func:`json.dumps` if saving as JSON.
        :raises: IOError when an invalid file suffix is used.

        """
        with open(filename, "w") as outfile:
            if filename.endswith(".json"):
                text = json.dumps(self.to_dict(), **json_kwargs)
            elif filename.endswith(".lst") or filename.endswith(".txt"):
                text = "\n".join(self)
            else:
                raise IOError("Invalid file type. Must be '.lst', '.txt', or '.json'")
            outfile.write(text)


class WordPool(object):
    """Handles operations for entire word pools.

    :param str path: Path to word pool.
    :param int num_lists: The number of lists to generate out of the entire
        pool.

    """
    def __init__(self, path, num_lists=1):
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

    def to_json(self, filename, indent=2):
        """Save to a JSON file.

        :param str filename:
        :param int indent: Spaces to indent with.

        """
        with open(filename, "w") as f:
            f.write(json.dumps(self.to_dict(), indent=indent))
