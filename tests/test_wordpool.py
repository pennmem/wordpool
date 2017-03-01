# -*- coding: utf-8 -*-

import os.path as osp
import shutil
from collections import Counter
import itertools
from tempfile import mkdtemp
import json
import pytest

from wordpool import WordList, WordPool


@pytest.fixture
def wordpool_en():
    yield osp.join("wordpool", "data", "ram_wordpool_en.txt")


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

    def test_save(self, wordpool_en, tempdir):
        words = WordList(wordpool_en)

        for suffix in [".lst", ".txt"]:
            filename = osp.join(tempdir, "out" + suffix)
            words.save(filename)
            with open(filename) as f:
                saved = f.read().split()
                assert WordList(saved) == words

        filename = osp.join(tempdir, "out.json")
        words.save(filename)
        with open(filename) as f:
            saved = json.load(f)
            assert "words" in saved
            assert saved["words"] == words
            assert "metadata" in saved
            assert saved["metadata"] == words.metadata

        with pytest.raises(IOError):
            filename = osp.join(tempdir, "out.wrong")
            words.save(filename)


class TestWordPool:
    def test_create(self, wordpool_en):
        pool = WordPool(wordpool_en, 25)
        with open(wordpool_en) as f:
            words = f.read().split()

        # Check types
        for l in pool.lists:
            assert isinstance(l, WordList)

        # Check shape
        assert len(pool.lists) is 25
        assert all([len(l) == 12 for l in pool.lists])

        # Check all words are present
        for word in words:
            assert any([word in lst for lst in pool.lists])

        # Check uniqueness
        counter = Counter(list(itertools.chain(*pool.lists)))
        assert len(list(counter.elements())) == len(words)

        # Check num_lists arg fails if wrong
        with pytest.raises(AssertionError):
            WordPool(wordpool_en, 26)
            WordPool(wordpool_en, 50)

        # Check shuffling performed
        pool2 = WordPool(wordpool_en, 25)
        for n in range(len(pool.lists)):
            assert pool.lists[n] != pool2.lists[n]

    def test_str(self, wordpool_en):
        pool = WordPool(wordpool_en)
        assert str(pool) == str(pool.lists)

    def test_getitem(self, wordpool_en):
        pool = WordPool(wordpool_en)
        for n in range(len(pool.lists)):
            assert pool[n] == pool.lists[n]

    def test_len(self, wordpool_en):
        pool = WordPool(wordpool_en)
        assert len(pool) == len(pool.lists)

    def test_iter(self, wordpool_en):
        for words in WordPool(wordpool_en):
            assert len(words) == 12
            for word in words:
                assert type(word) is str

    def test_save(self):
        pass
