import codecs
import json


def plaintext_to_json(txt_path, json_path=None, encoding="utf-8", indent=2):
    """Convert a pool of words contained in plaintext to JSON.

    Currently limited to whitespace-delimited text files.

    :param str txt_path: Path to .txt file.
    :param str json_path: Path to .json file or None to only return a dict.
    :param str encoding: Text encoding (default: "utf-8").
    :param str indent: Number of spaces to indent with (default: 2).
    :rtype: dict

    """
    with codecs.open(txt_path, encoding=encoding) as tfile:
        words = dict(pool=sorted(tfile.read().split()))

    if json_path is not None:
        with open(json_path, "w") as jfile:
            jfile.write(json.dumps(words, indent=2))

    return words
