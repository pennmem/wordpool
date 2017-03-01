# -*- coding: utf-8 -*-

import os.path as osp
import shutil
from collections import Counter
import itertools
from tempfile import mkdtemp
import json
import pytest
import numpy as np

from wordpool import WordList, WordPool


@pytest.fixture
def wordpool_en():
    yield osp.join("wordpool", "data", "ram_wordpool_en.txt")


@pytest.fixture
def wordpool_list():
    with open(osp.join("wordpool", "data", "ram_wordpool_en.txt")) as f:
        yield f.read().split()


@pytest.fixture
def tempdir():
    directory = mkdtemp()
    yield directory
    shutil.rmtree(directory, ignore_errors=True)


class TestWordList:
    def test_shuffle(self):
        num = 10
        words = WordList([str(n) for n in range(num)])
        res = words.shuffle()
        assert res is words
        assert len(res) is num
        for n in range(num):
            assert str(n) in res

    def test_to_dict(self):
        words = ["abc", "def"]
        meta = {"thing": 1}
        d = WordList(words, meta).to_dict()
        assert "metadata" in d
        assert "thing" in d["metadata"]
        assert "created" in d["metadata"]
        assert "words" in d
        assert d["words"] == words

    def test_to_json(self, wordpool_en, tempdir):
        words = WordList(wordpool_en)
        filename = osp.join(tempdir, "out.json")
        words.to_json(filename)
        with open(filename) as f:
            saved = json.load(f)
            assert "words" in saved
            assert saved["words"] == words
            assert "metadata" in saved
            assert saved["metadata"] == words.metadata

    def test_to_text(self, wordpool_en, tempdir):
        words = WordList(wordpool_en)
        filename = osp.join(tempdir, "out.txt")
        words.to_text(filename)
        with open(filename) as f:
            saved = f.read().split()
            assert WordList(saved) == words


class TestWordPool:
    def test_create(self, wordpool_list):
        pool = WordPool([wordpool_list])
        assert WordList(wordpool_list) == pool.lists[0]

    def test_str(self, wordpool_list):
        pool = WordPool([wordpool_list])
        assert str(pool) == str(pool.lists)

    def test_getitem(self, wordpool_list):
        pool = WordPool([wordpool_list])
        for n in range(len(pool.lists)):
            assert pool[n] == pool.lists[n]

    def test_len(self, wordpool_list):
        pool = WordPool([wordpool_list])
        assert len(pool) == len(pool.lists)

    def test_iter(self, wordpool_list):
        for words in WordPool([wordpool_list]):
            for word in words:
                assert type(word) is str

    def test_shuffle_lists(self, wordpool_list):
        words = np.array(wordpool_list).reshape((25, 12))
        pool = WordPool(words.tolist())
        pool.shuffle_lists()
        for n, list_ in enumerate(pool.lists):
            assert words[n].tolist() != list_

    def test_to_dict(self, wordpool_list):
        pool = WordPool([wordpool_list])
        words = pool.to_dict()
        assert len(words) == 1
        assert "lists" in words
        assert isinstance(words["lists"], list)
        for list_ in words["lists"]:
            assert isinstance(list_, dict)
            assert "metadata" in list_
            assert "words" in list_
            assert len(list_["words"]) == 300

    def test_to_json(self, wordpool_list, tempdir):
        filename = osp.join(tempdir, "out.json")
        pool = WordPool([wordpool_list])
        pool.to_json(filename)
        with open(filename) as f:
            saved = json.load(f)
            assert len(saved) == 1
            assert "lists" in saved
