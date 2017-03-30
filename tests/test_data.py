import os.path as osp
from wordpool.data import read_list


def test_read_list():
    with open(osp.join("wordpool", "data", "ram_wordpool_en.txt")) as f:
        pool = f.read().split()

    words = read_list("ram_wordpool_en.txt")
    assert words == pool
