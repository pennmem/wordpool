# -*- coding: utf-8 -*-

import os.path as osp
import subprocess
import numpy as np
import pytest

import wordpool

here = osp.realpath(osp.dirname(__file__))


@pytest.fixture
def pool(language="en"):
    yield wordpool.load("ram_wordpool_{:s}.txt".format(language))


@pytest.fixture
def catpool(language="en"):
    yield wordpool.load("ram_categorized_{:s}.txt".format(language))


def test_create(pool, catpool):
    assert "word" in pool
    assert "word" in catpool
    assert "category" in catpool
    output = subprocess.check_output("git rev-parse --show-toplevel".split())
    root = output.decode().strip()
    other = wordpool.load(osp.join(root, "wordpool", "data", "ram_wordpool_en.txt"), False)
    assert "word" in other


def test_assign_list_numbers(catpool):
    df = catpool.copy()
    assigned = wordpool.assign_list_numbers(catpool, 25)
    assert "listno" in assigned.columns
    assert "word" in assigned.columns
    assert "category" in assigned.columns
    assert all(list(range(25)) == assigned.listno.unique())
    assert all(df.word == assigned.word)
    assert all(df.category == assigned.category)


def test_shuffle_words(pool, catpool):
    df = pool.copy()
    catdf = catpool.copy()

    words = wordpool.shuffle_words(pool)
    assert any((words != df).any())
    catwords = wordpool.shuffle_words(catpool)
    assert any((catwords != catdf).any())
    for i, row in catdf.iterrows():
        category = catwords.category[catwords.word == row.word].iloc[0]
        assert category == row.category
    assert catwords.index[0] == 0


def test_shuffle_within_lists(pool, catpool):
    df = pool.copy()
    catdf = catpool.copy()

    with pytest.raises(RuntimeError):
        words = wordpool.shuffle_within_lists(df)
    with pytest.raises(RuntimeError):
        catwords = wordpool.shuffle_within_lists(catdf)

    df = wordpool.assign_list_numbers(df, 25)
    catdf = wordpool.assign_list_numbers(catdf, 25)
    words = wordpool.shuffle_within_lists(df)
    catwords = wordpool.shuffle_within_lists(catdf)

    for listno in words.listno.unique():
        assert not (words[words.listno == listno].word == df[words.listno == listno].word).all()

    for listno in catwords.listno.unique():
        assert not (catwords[catwords.listno == listno].word == catdf[words.listno == listno].word).all()
