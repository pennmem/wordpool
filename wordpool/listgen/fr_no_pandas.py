from __init__ import assign_list_numbers_no_pandas

def concatenate_session_lists(practice_list, word_list, words_per_list, num_lists):
    """Takes a practice list and a list of all the words for the session.  Combines them appropriately and adds list numbers.  Does not shuffle.  Shuffle beforehand please.

    :param practice_list: list of words for practice session
    :param int num_lists: Total number of lists excluding the practice list.
    :returns: list of (word, listno) pairs
    """

    assert len(word_list) == words_per_list * num_lists
    practice_list = assign_list_numbers_no_pandas(practice_list, 1)
    word_list = assign_list_numbers_no_pandas(word_list, num_lists, start=1)
    return practice_list + word_list
