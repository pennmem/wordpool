# -*- coding: utf-8 -*-

import os.path as osp
import shutil
from tempfile import mkdtemp
import random
from copy import deepcopy
import pytest

import numpy as np
import pandas as pd

from wordpool import WordPool

here = osp.realpath(osp.dirname(__file__))


@pytest.fixture
def pool(language="en"):
    path = osp.join(here, "..", "wordpool", "data", "ram_wordpool_{:s}.txt".format(language))
    yield str(path)


@pytest.fixture
def catpool(language="en"):
    path = osp.join(here, "..", "wordpool", "data", "ram_categorized_{:s}.txt".format(language))
    yield str(path)


@pytest.fixture
def tempdir():
    directory = mkdtemp()
    yield directory
    shutil.rmtree(directory, ignore_errors=True)


class TestWordPool:
    def test_create(self, pool, catpool):
        words = WordPool(pool)
        assert 'word' in words.df.columns

        words = WordPool(catpool)
        assert 'word' in words.df.columns
        assert "category" in words.df.columns

    def test_str(self, pool):
        words = WordPool(pool)
        assert str(words) == str(words.df)

    def test_len(self, pool):
        words = WordPool(pool)
        assert len(words) == len(words.df)

    def test_iter(self, pool):
        for words in WordPool(pool):
            assert "word" in words.index
            assert isinstance(words.word, str)

    def test_shuffle_words(self, pool, catpool):
        words = WordPool(pool)
        df = words.df.copy()
        catwords = WordPool(catpool)
        catdf = catwords.df.copy()

        # shuffling all
        words.shuffle_words()
        assert any((words != df).any())
        catwords.shuffle_words()
        assert any((catwords != catdf).any())
        for i, row in catdf.iterrows():
            category = catwords.df.category[catwords.df.word == row.word].iloc[0]
            assert category == row.category
        assert catwords.df.index[0] == 0

        # keeping some fixed

    # def test_shuffle_within_lists(self, pool):
    #     words = np.array(pool).reshape((25, 12))
    #     pool = WordPool(words.tolist())
    #     pool.shuffle_within_lists()
    #     for n, list_ in enumerate(pool.lists):
    #         assert words[n].tolist() != list_
    #
    #     pool = WordPool(words.tolist())
    #     frozen = random.sample(range(len(pool.lists)), 5)
    #     old_pool = deepcopy(pool)
    #     pool.shuffle_within_lists(frozen)
    #     for n in frozen:
    #         assert old_pool.lists[n] == pool.lists[n]
    #
    # def test_to_dict(self, pool):
    #     pool = WordPool([pool])
    #     words = pool.to_dict()
    #     assert len(words) == 1
    #     assert "lists" in words
    #     assert isinstance(words["lists"], list)
    #     for list_ in words["lists"]:
    #         assert isinstance(list_, dict)
    #         assert "metadata" in list_
    #         assert "words" in list_
    #         assert len(list_["words"]) == 300
