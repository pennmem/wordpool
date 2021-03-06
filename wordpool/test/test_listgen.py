import os
import os.path as osp
import shutil
from contextlib import contextmanager
import pytest

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

import wordpool
from wordpool import listgen, exc


@contextmanager
def subdir(parent, name="sub"):
    path = osp.join(str(parent), name)
    os.mkdir(path)
    yield path
    shutil.rmtree(path, ignore_errors=True)


def test_write_wordpool(tmpdir):
    fn = listgen.write_wordpool_txt

    # unsupported language
    with pytest.raises(exc.LanguageError):
        fn(tmpdir, "DA")

    # missing rec words for supported language
    with pytest.raises(exc.LanguageError):
        fn(tmpdir, "SP", True)

    # writing without lures
    with subdir(tmpdir) as path:
        ret = fn(path, "EN")
        assert len(os.listdir(path)) == 1
        assert len(ret) == 1
        assert ret[0] == osp.join(path, "RAM_wordpool.txt")

        with open(ret[0]) as f:
            words = pd.Series([l.strip() for l in f.readlines()])
            assert (words == wordpool.load("ram_wordpool_en.txt").word).all()

    # Writing with lures
    with subdir(tmpdir) as path:
        ret = fn(path, "EN", True)
        assert len(os.listdir(path)) == 2
        assert len(ret) == 2
        assert ret[0] == osp.join(path, "RAM_wordpool.txt")
        assert ret[1] == osp.join(path, "RAM_lurepool.txt")

        # targets
        with open(ret[0]) as f:
            words = pd.Series([l.strip() for l in f.readlines()])
            assert (words == wordpool.load("ram_wordpool_en.txt").word).all()

        # lures
        with open(ret[1]) as f:
            words = pd.Series([l.strip() for l in f.readlines()])
            assert (words == wordpool.load("REC1_lures_en.txt").word).all()


@pytest.mark.fr
class TestFR:
    def test_generate_session_pool(self):
        # Test basic things like types and lengths being correct
        for language in "EN", "SP":
            session = listgen.fr.generate_session_pool(language=language)
            assert type(session) is pd.DataFrame
            # assert len(session.word) == 26*12 # number of words depends on the contents of the wordpool file

            for listno in session.listno.unique():
                df = session[session.listno == listno]
                assert type(df) is pd.DataFrame
                assert len(df) is 12

        with pytest.raises(AssertionError):
            listgen.fr.generate_session_pool(7)
        with pytest.raises(AssertionError):
            listgen.fr.generate_session_pool(num_lists=27)
        with pytest.raises(AssertionError):
            listgen.fr.generate_session_pool(language="DA")

        # Test uniqueness
        session1 = listgen.fr.generate_session_pool()
        session2 = listgen.fr.generate_session_pool()
        for n in session1.listno.unique():
            first = session1[session1.listno == n]
            second = session2[session2.listno == n]
            assert not (first.word == second.word).all()  # practice lists should be shuffled, too!

    def test_assign_list_types(self):
        session = listgen.fr.generate_session_pool()
        session = listgen.assign_list_types(session, 4, 7, 11, 4)
        words_per_list = 12

        assert 'stim_channels' in session
        assert all(session[session.stim_channels.notnull()].stim_channels == (0,))

        grouped = session.groupby("phase_type")
        counts = grouped.count()
        assert len(counts.index) == 4
        assert counts.loc["BASELINE"].listno / words_per_list == 4
        assert counts.loc["NON-STIM"].listno / words_per_list == 7
        assert counts.loc["STIM"].listno / words_per_list == 11
        assert counts.loc["PS"].listno / words_per_list == 4

        assert all(session[session["phase_type"] == "PRACTICE"].listno == 0)

        for n in range(1, 4):
            assert n in session[session["phase_type"] == "BASELINE"].listno.unique()

        for n in range(4, 8):
            assert n in session[session["phase_type"] == "PS"].listno.unique()

        for n in range(8, 26):
            assert session[session.listno == n]["phase_type"].isin(["STIM", "NON-STIM"]).all()

    def test_assign_multistim(self):
        words_per_list = 12
        session = listgen.fr.generate_session_pool(num_lists=26)
        stimspec = {
            (0,): 4,
            (1,): 5,
            (0, 1): 2
        }

        with pytest.raises(AssertionError):
            listgen.assign_multistim(session, {1: 5})

        with pytest.raises(AssertionError):
            listgen.assign_multistim(session, stimspec)

        session = listgen.assign_list_types(session, 4, 7, 11, 4)
        multistim = listgen.assign_multistim(session, stimspec)

        assert 'stim_channels' in multistim.columns
        for key, num in stimspec.items():
            assert key in list(multistim.stim_channels.unique())
            assert len(multistim[multistim.stim_channels == key].stim_channels) / words_per_list == num

    def test_generate_rec1_blocks(self):
        pool = listgen.fr.generate_session_pool()
        assigned = listgen.assign_list_types(pool, 4, 6, 16, 0)
        lures = wordpool.load("REC1_lures_en.txt")
        blocks = listgen.generate_rec1_blocks(assigned, lures)

        assert isinstance(blocks, pd.DataFrame)
        assert not all([s == u for s, u in zip(sorted(blocks.listno), blocks.listno)])

        blocks2 = listgen.generate_rec1_blocks(assigned, lures)
        for n in range(len(blocks.word)):
            if blocks.word.iloc[0] != blocks2.word.iloc[0]:
                break
        assert n < len(blocks.word)

        # this should be the original index before being reset
        assert "index" in blocks.columns

    @pytest.mark.parametrize('iteration', range(5))
    def test_generate_learn1_blocks(self, iteration):
        session = listgen.fr.generate_session_pool()
        pool = listgen.assign_list_types(session, 4, 6, 16)
        stimspec = {
            (0,): 5,
            (1,): 5,
            (0, 1): 6
        }
        pool = listgen.assign_multistim(pool, stimspec)
        blocks = listgen.generate_learn1_blocks(pool, 2, 2, (0, 1))

        stim_channels = blocks.stim_channels.unique().tolist()
        assert (0, 1) in stim_channels
        assert (0,) not in stim_channels
        assert (1,) not in stim_channels
        assert len(blocks.blockno.unique()) == 4
        assert len(blocks.listno.unique()) == 4

        # Verify block list numbers
        assert len(blocks.block_listno.unique()) == 16
        assert list(blocks.block_listno.unique()) == list(range(16))
        block_listnos = []
        for blockno in range(4):
            block = blocks[blocks.blockno == blockno]
            block_listnos.append(sorted(list(block.block_listno.unique())))
        assert [block_listnos[i] == block_listnos[i + 1] for i in range(3)]

        blocks = [blocks[blocks.blockno == n].reset_index() for n in range(4)]
        for i, block1 in enumerate(blocks):
            for j, block2 in enumerate(blocks):
                if i == j:
                    continue
                with pytest.raises(AssertionError):
                    assert_frame_equal(block1, block2)


@pytest.mark.catfr
class TestCatFR:
    @property
    def catpool(self):
        return wordpool.load("ram_categorized_en.txt")

    def test_assign_list_numbers(self):
        # must assign word numbers first
        with pytest.raises(AssertionError):
            listgen.catfr.assign_list_numbers(self.catpool)

        pool = listgen.catfr.assign_word_numbers(self.catpool)
        assigned = listgen.catfr.assign_list_numbers(pool)

        assert len(assigned) == 312
        assert len(assigned.word.unique()) == 312
        assert "listno" in assigned.columns
        assert len(assigned[assigned.listno < 0]) == 0, str(assigned)
        counts = assigned.groupby("listno").listno.count()
        for count in counts:
            assert counts[count] == 12

    def test_sort_pairs(self):
        pool = self.catpool.copy()
        with pytest.raises(AssertionError):
            listgen.catfr.sort_pairs(pool)
        with pytest.raises(AssertionError):
            listgen.catfr.sort_pairs(listgen.catfr.assign_word_numbers(pool))

        pool = listgen.catfr.sort_pairs(listgen.catfr.assign_list_numbers(
            listgen.catfr.assign_word_numbers(pool)))

        # check uniqueness and that all words/categories are used
        assert len(pool.word.unique()) == 312
        assert len(pool.category.unique()) == 26

        # check that words come in pairs
        for n in pool.index[::2]:
            assert pool.category[n] == pool.category[n + 1]

        # check that last middle categories don't repeat
        for n in range(5, len(pool), 12):
            assert pool.category[n] != pool.category[n + 1]

    def test_generate_cat_session_pool(self):
        with pytest.raises(exc.LanguageError):
            listgen.catfr.generate_session_pool(language="DA")

        pool = listgen.catfr.generate_session_pool()
        assert len(pool) == 312
        assert "listno" in pool
        assert "category" in pool
        assert not any(pool.category.isnull())

        # no repeated words and all words used
        assert len(pool.word.unique()) == 312

        # all categories used
        assert len(pool.category.unique()) == 26

        # uniqueness
        pool2 = listgen.catfr.generate_session_pool()
        for n in pool.listno.unique():
            first = pool[pool.listno == n]
            second = pool2[pool2.listno == n]
            assert not (first.word == second.word).all()


@pytest.mark.pal
class TestPAL:
    @staticmethod
    def equal_pairs(a, b):
        backward = np.array(
            [(b.loc[b.word2 == a.loc[i].word1].word1 == a.loc[i].word2).any()
             for i in a.index]).astype(np.bool)
        forward = np.array(
            [(b.loc[b.word1 == a.loc[i].word1].word2 == a.loc[i].word2).any()
             for i in a.index]).astype(np.bool)
        return backward | forward

    def test_generate_session_pool(self):
        with pytest.raises(AssertionError):
            listgen.pal.generate_n_session_pairs(1, n_pairs=8)
        with pytest.raises(AssertionError):
            listgen.pal.generate_n_session_pairs(1, n_lists=20)
        with pytest.raises(KeyError):
            listgen.pal.generate_n_session_pairs(1, language='HE')

        pool = listgen.pal.generate_n_session_pairs(1)[0]

        for field in ['word1', 'word2', 'listno', 'type']:
            assert field in pool.columns

        practice_pairs = pool.loc[pool.type == 'PRACTICE']
        assert len(practice_pairs)*2 == np.unique(practice_pairs[['word1', 'word2']].values).size

        assert len(pool)*2 == np.unique(pool[['word1', 'word2']].values).size

        for _, list_pairs in pool.groupby('listno'):
            assert len(list_pairs) == 6

    def test_assign_cue_position(self):
        pool = listgen.pal.generate_n_session_pairs(1)[0]
        cue_positions_by_list = [listgen.pal.assign_cues(words) for _, words in pool.groupby('listno')]
        for list_cue_positions in cue_positions_by_list:
            assert sum([x == 'word1' for x in list_cue_positions]) == len(list_cue_positions)/2
            assert sum([x == 'word2' for x in list_cue_positions]) == len(list_cue_positions)/2

    def test_assigned_cue_positions(self):
        pool = listgen.pal.generate_n_session_pairs(1)[0]

        for _, words_by_list in pool.groupby('listno'):
            assert (words_by_list['cue_pos'] == 'word1').sum() == len(words_by_list)/2
            assert (words_by_list['cue_pos'] == 'word2').sum() == len(words_by_list)/2

    def test_uniqueness(self):
        wordpools = listgen.pal.generate_n_session_pairs(10)
        for i in range(10):
            for j in range(i):
                pool1 = wordpools[i]
                pool2 = wordpools[j]
                assert not self.equal_pairs(pool1.loc[pool1.type != 'PRACTICE'],
                                            pool2.loc[pool2.type != 'PRACTICE']).any()
