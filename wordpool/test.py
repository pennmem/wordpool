# -*- coding: utf-8 -*-

import os.path as osp
import shutil
from tempfile import mkdtemp
import pytest

import wordpool

here = osp.realpath(osp.dirname(__file__))


@pytest.fixture
def pool(language="en"):
    yield wordpool.load("ram_wordpool_{:s}.txt".format(language))


@pytest.fixture
def catpool(language="en"):
    yield wordpool.load("ram_categorized_{:s}.txt".format(language))


@pytest.fixture
def tempdir():
    directory = mkdtemp()
    yield directory
    shutil.rmtree(directory, ignore_errors=True)


def test_create(pool, catpool):
    assert "word" in pool
    assert "word" in catpool
    assert "category" in catpool


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

    # shuffling all
    words = wordpool.shuffle_words(pool)
    assert any((words != df).any())
    catwords = wordpool.shuffle_words(catpool)
    assert any((catwords != catdf).any())
    for i, row in catdf.iterrows():
        category = catwords.category[catwords.word == row.word].iloc[0]
        assert category == row.category
    assert catwords.index[0] == 0

    # TODO: keeping some fixed
