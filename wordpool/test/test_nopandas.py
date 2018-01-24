import os
import os.path as osp
import shutil
from contextlib import contextmanager
import pytest

import wordpool
from wordpool import nopandas

def a_couple_words():
    return [{"word": "one"}, {"word": "two"}]

def a_couple_more_words():
    return [{"word": "three"}, {"word": "four"}]

def ten_words():
    return [{"word": "five"}, {"word": "six"}, {"word": "seven"}, {"word": "eight"}, {"word": "nine"}, {"word": "ten"}, {"word": "eleven"}, {"word": "twelve"}, {"word": "thirteen"}, {"word": "fourteen"}]


@pytest.mark.nopandas
class TestConcatenateSessionLists:
    def test_raises_list_length_error(self):
        four_words = a_couple_words() + a_couple_more_words()
        with pytest.raises(AssertionError):
            nopandas.assign_list_numbers_from_word_list(four_words, 3, 3)

    def test_assigns_listnos(self):
        four_words = a_couple_words() + a_couple_more_words()
        result = nopandas.assign_list_numbers_from_word_list(four_words, 2)
        assert result == [{"word": "one", "listno": 0}, {"word": "two", "listno": 0}, {"word": "three", "listno": 1}, {"word": "four", "listno": 1}]

    def test_empty_inputs(self):
        result = nopandas.assign_list_numbers_from_word_list({}, 0)
        assert result == []

@pytest.mark.nopandas
class TestIntegratedNoPandasFunctions:
    def test_fr6_wordpool(self):
        
        #here is an example of how to create an fr6 wordpool, which uses all the nopandas functions
        
        #first, load lists of dictionaries with 'word' keys and values containing the word, such as 'dog'
        word_list = a_couple_words() + ten_words()
        
        #shuffling is not performed in no pandas functions.  to meet the fr6 requirements, shuffle lists before
        #passing them to nopandas functions. likes this:
        #word_list.shuffle()
        #lists are not shuffled here in order to facilitate testing
        
        #this will take a list of dictionaries for the practice list, and another for the rest of the lists
        #it will concatenate them into one list of dictionaries with list numbers assigned under the key 'listno'
        #list numbers start from 0
        words_with_listnos = nopandas.assign_list_numbers_from_word_list(word_list, 6)
        #two is the number of words per list, and 5 is the number of lists, which excludes the practice list

        assert words_with_listnos == [{"word": "one", "listno": 0},
                                      {"word": "two", "listno": 0},
                                      {"word": "five", "listno": 1},
                                      {"word": "six", "listno": 1},
                                      {"word": "seven", "listno": 2},
                                      {"word": "eight", "listno": 2},
                                      {"word": "nine", "listno": 3},
                                      {"word": "ten", "listno": 3},
                                      {"word": "eleven", "listno": 4},
                                      {"word": "twelve", "listno": 4},
                                      {"word": "thirteen", "listno": 5},
                                      {"word": "fourteen", "listno": 5}]

        #next step is to assign list types.  list types proceed from practice, to baseline, to ps, and then stim
        #and nostim lists.  the stim and nostim lists are randomly interleaved, so give them to nopandas in the
        #form of a list of "STIM" and "NON-STIM" strings pre-interleaved
        stim_nostim_list = ["STIM"] * 2 + ["NON-STIM"] * 1
        #stim_nostim_list.shuffle() you would shuffle this if this weren't a test

        #this will make one baseline, one ps, and 3 stim/nonstim lists.
        #FR6 has 3 baseline, 0 ps, and 22 stim/nonstim.
        words_with_listtypes = nopandas.assign_list_types_from_type_list(words_with_listnos, 2, stim_nostim_list, num_ps=1)
        #this also adds stim_channels entries, None for non-stim/baseline/practice, or (0,) for stim

        assert words_with_listtypes == [{"word": "one", "listno": 0, "type":"BASELINE", "stim_channels": None},
                                        {"word": "two", "listno": 0, "type":"BASELINE", "stim_channels": None},
                                        {"word": "five", "listno": 1, "type":"BASELINE", "stim_channels": None},
                                        {"word": "six", "listno": 1, "type":"BASELINE", "stim_channels": None},
                                        {"word": "seven", "listno": 2, "type":"PS", "stim_channels": None},
                                        {"word": "eight", "listno": 2, "type":"PS", "stim_channels": None},
                                        {"word": "nine", "listno": 3, "type":"STIM", "stim_channels": (0, )},
                                        {"word": "ten", "listno": 3, "type":"STIM", "stim_channels": (0, )},
                                        {"word": "eleven", "listno": 4, "type":"STIM", "stim_channels": (0, )},
                                        {"word": "twelve", "listno": 4, "type":"STIM", "stim_channels": (0, )},
                                        {"word": "thirteen", "listno": 5, "type":"NON-STIM", "stim_channels": None},
                                        {"word": "fourteen", "listno": 5, "type":"NON-STIM", "stim_channels": None}]

        #third step is to assign stim channels beyond simply (0, ) each time.  pass in a list of channels, and
        #they will be distributed in order to each of the stim lists
        stim_channels_list = [(0, 1)] * 1 + [(0, )] * 1

        words_with_multistim = nopandas.assign_multistim_from_stim_channels_list(words_with_listtypes, stim_channels_list)

        assert words_with_multistim == [{"word": "one", "listno": 0, "type":"BASELINE", "stim_channels": None},
                                        {"word": "two", "listno": 0, "type":"BASELINE", "stim_channels": None},
                                        {"word": "five", "listno": 1, "type":"BASELINE", "stim_channels": None},
                                        {"word": "six", "listno": 1, "type":"BASELINE", "stim_channels": None},
                                        {"word": "seven", "listno": 2, "type":"PS", "stim_channels": None},
                                        {"word": "eight", "listno": 2, "type":"PS", "stim_channels": None},
                                        {"word": "nine", "listno": 3, "type":"STIM", "stim_channels": (0, 1)},
                                        {"word": "ten", "listno": 3, "type":"STIM", "stim_channels": (0, 1)},
                                        {"word": "eleven", "listno": 4, "type":"STIM", "stim_channels": (0, )},
                                        {"word": "twelve", "listno": 4, "type":"STIM", "stim_channels": (0, )},
                                        {"word": "thirteen", "listno": 5, "type":"NON-STIM", "stim_channels": None},
                                        {"word": "fourteen", "listno": 5, "type":"NON-STIM", "stim_channels": None}]

        #finally, extract the learning blocks and append them to the main lists.  extract_blocks takes a list of
        #the blocks you want to repeat, and a number of blocks to divide them into.  fr6 calls for four blocks of
        #four lists each, and only repeats non-stim and (0, 1) stim lists, but that is not enforced here
        
        listnos_repetion_pattern = [3, 4, 5, 5, 4, 3, 4, 5, 3]
        
        #extract_blocks will add blockno entries to represent which learning block (starting from 0) and
        #block_listno to represent how many lists have gone by so far in the learning blocks (also starting
        #from 0)
        words_with_learning_blocks = words_with_multistim + nopandas.extract_blocks(words_with_multistim, listnos_repetion_pattern, 3)
        #repeat the blocks 3, 4, and 5 in various orders three times as given by listnos_repetition pattern.
        #because they are repeated three times, this means they are divided into three blocks.  that is the
        #meaning of the 3 parameter.

        assert words_with_learning_blocks == [{"word": "one", "listno": 0, "type":"BASELINE", "stim_channels": None},
                                              {"word": "two", "listno": 0, "type":"BASELINE", "stim_channels": None},
                                              {"word": "five", "listno": 1, "type":"BASELINE", "stim_channels": None},
                                              {"word": "six", "listno": 1, "type":"BASELINE", "stim_channels": None},
                                              {"word": "seven", "listno": 2, "type":"PS", "stim_channels": None},
                                              {"word": "eight", "listno": 2, "type":"PS", "stim_channels": None},
                                              {"word": "nine", "listno": 3, "type":"STIM", "stim_channels": (0, 1)},
                                              {"word": "ten", "listno": 3, "type":"STIM", "stim_channels": (0, 1)},
                                              {"word": "eleven", "listno": 4, "type":"STIM", "stim_channels": (0, )},
                                              {"word": "twelve", "listno": 4, "type":"STIM", "stim_channels": (0, )},
                                              {"word": "thirteen", "listno": 5, "type":"NON-STIM", "stim_channels": None},
                                              {"word": "fourteen", "listno": 5, "type":"NON-STIM", "stim_channels": None},
                                              {"word": "nine", "listno": 3, "type":"STIM", "stim_channels": (0, 1), "blockno": 0, "block_listno": 0},
                                              {"word": "ten", "listno": 3, "type":"STIM", "stim_channels": (0, 1), "blockno": 0, "block_listno": 0},
                                              {"word": "eleven", "listno": 4, "type":"STIM", "stim_channels": (0, ), "blockno": 0, "block_listno": 1},
                                              {"word": "twelve", "listno": 4, "type":"STIM", "stim_channels": (0, ), "blockno": 0, "block_listno": 1},
                                              {"word": "thirteen", "listno": 5, "type":"NON-STIM", "stim_channels": None, "blockno": 0, "block_listno": 2},
                                              {"word": "fourteen", "listno": 5, "type":"NON-STIM", "stim_channels": None, "blockno": 0, "block_listno": 2},
                                              {"word": "thirteen", "listno": 5, "type":"NON-STIM", "stim_channels": None, "blockno": 1, "block_listno": 3},
                                              {"word": "fourteen", "listno": 5, "type":"NON-STIM", "stim_channels": None, "blockno": 1, "block_listno": 3},
                                              {"word": "eleven", "listno": 4, "type":"STIM", "stim_channels": (0, ), "blockno": 1, "block_listno": 4},
                                              {"word": "twelve", "listno": 4, "type":"STIM", "stim_channels": (0, ), "blockno": 1, "block_listno": 4},
                                              {"word": "nine", "listno": 3, "type":"STIM", "stim_channels": (0, 1), "blockno": 1, "block_listno": 5},
                                              {"word": "ten", "listno": 3, "type":"STIM", "stim_channels": (0, 1), "blockno": 1, "block_listno": 5},
                                              {"word": "eleven", "listno": 4, "type":"STIM", "stim_channels": (0, ), "blockno": 2, "block_listno": 6},
                                              {"word": "twelve", "listno": 4, "type":"STIM", "stim_channels": (0, ), "blockno": 2, "block_listno": 6},
                                              {"word": "thirteen", "listno": 5, "type":"NON-STIM", "stim_channels": None, "blockno": 2, "block_listno": 7},
                                              {"word": "fourteen", "listno": 5, "type":"NON-STIM", "stim_channels": None, "blockno": 2, "block_listno": 7},
                                              {"word": "nine", "listno": 3, "type":"STIM", "stim_channels": (0, 1), "blockno": 2, "block_listno": 8},
                                              {"word": "ten", "listno": 3, "type":"STIM", "stim_channels": (0, 1), "blockno": 2, "block_listno": 8}]

    def test_amplitude_index_assignmnt(self):
        word_list = a_couple_words() + a_couple_more_words() + ten_words()

        pool = words_with_listnos = nopandas.assign_list_numbers_from_word_list(word_list, 7)

        stim_nostim_list = ["NON-STIM"] + ["STIM"] * 6
        words_with_listtypes = nopandas.assign_list_types_from_type_list(pool, 0, stim_nostim_list)

        amplitude_index_list = [1, 2, 3, 1, 3, 2]
        words_with_amplitude_index = nopandas.assign_amplitudes_from_amplitude_index_list(words_with_listtypes, amplitude_index_list)
        assert words_with_amplitude_index == [{"word": "one", "listno": 0, "type":"NON-STIM", "stim_channels": None},
                                             {"word": "two", "listno": 0, "type":"NON-STIM", "stim_channels": None},
                                             {"word": "three", "listno": 1, "type":"STIM", "stim_channels": (0, ), "amplitude_index": 1},
                                             {"word": "four", "listno": 1, "type":"STIM", "stim_channels": (0, ), "amplitude_index": 1},
                                             {"word": "five", "listno": 2, "type":"STIM", "stim_channels": (0, ), "amplitude_index": 2},
                                             {"word": "six", "listno": 2, "type":"STIM", "stim_channels": (0, ), "amplitude_index": 2},
                                             {"word": "seven", "listno": 3, "type":"STIM", "stim_channels": (0, ), "amplitude_index": 3},
                                             {"word": "eight", "listno": 3, "type":"STIM", "stim_channels": (0, ), "amplitude_index": 3},
                                             {"word": "nine", "listno": 4, "type":"STIM", "stim_channels": (0, ), "amplitude_index": 1},
                                             {"word": "ten", "listno": 4, "type":"STIM", "stim_channels": (0, ), "amplitude_index": 1},
                                             {"word": "eleven", "listno": 5, "type":"STIM", "stim_channels": (0, ), "amplitude_index": 3},
                                             {"word": "twelve", "listno": 5, "type":"STIM", "stim_channels": (0, ), "amplitude_index": 3},
                                             {"word": "thirteen", "listno": 6, "type":"STIM", "stim_channels": (0, ), "amplitude_index": 2},
                                             {"word": "fourteen", "listno": 6, "type":"STIM", "stim_channels": (0, ), "amplitude_index": 2}]