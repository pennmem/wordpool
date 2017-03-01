import os.path as osp
import json
from wordpool import io


def test_plaintext_to_json():
    root = osp.join("wordpool", "data")
    txtfile = osp.join(root, "ram_wordpool_en.txt")
    jsonfile = osp.join(root, "ram_wordpool_en.json")

    with open(txtfile) as f:
        txt_contents = f.read().split()

    with open(jsonfile) as f:
        json_contents = f.read().split()

    words = io.plaintext_to_json(txtfile)
    assert isinstance(words, dict)
    assert "pool" in words
    assert words["pool"] == txt_contents
