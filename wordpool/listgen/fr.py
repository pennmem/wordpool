"""FR list generation."""

try:
    import pandas as pd
except:
    pd = None

try:
    from .. import load, shuffle_words, assign_list_numbers, pool_dataframe_to_pool_list
except:
    load = shuffle_words = assign_list_numbers = pool_dataframe_to_pool_list

if (load):
    RAM_LIST_EN = load("ram_wordpool_en.txt")
    RAM_LIST_SP = load("ram_wordpool_sp.txt")

    CAT_LIST_EN = load("ram_categorized_en.txt")
    CAT_LIST_SP = load("ram_categorized_sp.txt")

    PRACTICE_LIST_EN = load("practice_en.txt")
    PRACTICE_LIST_SP = load("practice_sp.txt")

def generate_session_pool(words_per_list=12, num_lists=25,
                          language="EN"):
    """Generate the pool of words for a single task session. This does *not*
    assign stim, no-stim, or PS metadata since this part depends on the
    experiment.

    :param int words_per_list: Number of words in each list.
    :param int num_lists: Total number of lists excluding the practice list.
    :param str language: Session language (``EN`` or ``SP``).
    :returns: Word pool
    :rtype: pd.DataFrame

    """
    global RAM_LIST_EN, PRACTICE_LIST_EN
    assert language in ("EN", "SP")

    practice = PRACTICE_LIST_EN if language == "EN" else PRACTICE_LIST_SP
    practice["type"] = "PRACTICE"
    practice["listno"] = 0
    practice = shuffle_words(practice).reset_index(drop=True)

    words = RAM_LIST_EN if language == "EN" else RAM_LIST_SP
    assert len(words) == words_per_list * num_lists
    words = shuffle_words(words).reset_index(drop=True)
    
    practice_list = pool_dataframe_to_pool_list(practice)
    word_list = pool_dataframe_to_pool_list(words)
    
    pool_list = concatenate_session_lists(practice_list, word_list, words_per_list, num_lists)
    df = pd.DataFrame(pool_list)
    df.rename(columns = {0:"word", 1:"listno"}, inplace = True)
    return df

def concatenate_session_lists(practice_list, word_list, words_per_list, num_lists):
    """Takes a practice list and a list of all the words for the session.  Combines them appropriately and adds list numbers.  Does not shuffle.  Shuffle beforehand please.
        
        :param practice_list: list of words for practice session
        :param int num_lists: Total number of lists excluding the practice list.
        :returns: list of (word, listno) pairs
        """
    
    assert len(word_list) == words_per_list * num_lists
    practice_list = assign_list_numbers(practice_list, 1)
    word_list = assign_list_numbers(word_list, num_lists, start=1)
    return practice_list + word_list
