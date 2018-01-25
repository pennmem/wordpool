"""FR list generation."""

from .. import load, shuffle_words, pool_dataframe_to_pool_list, pool_list_to_pool_dataframe
from ..nopandas import assign_list_numbers_from_word_list

RAM_LIST_EN = load("ram_wordpool_en.txt")
RAM_LIST_SP = load("ram_wordpool_sp.txt")

CAT_LIST_EN = load("ram_categorized_en.txt")
CAT_LIST_SP = load("ram_categorized_sp.txt")


def generate_session_pool(num_lists=26, language="EN"):
    """Generate the pool of words for a single task session. This does *not*
    assign stim, no-stim, or PS metadata since this part depends on the
    experiment.

    :param int num_lists: Total number of lists excluding the practice list.
    :param str language: Session language (``EN`` or ``SP``).
    :returns: Word pool
    :rtype: pd.DataFrame

    """
    global RAM_LIST_EN
    assert language in ("EN", "SP")

    words = RAM_LIST_EN if language == "EN" else RAM_LIST_SP
    words = shuffle_words(words).reset_index(drop=True)

    word_list = pool_dataframe_to_pool_list(words)

    pool_list = assign_list_numbers_from_word_list(word_list, num_lists)
    df = pool_list_to_pool_dataframe(pool_list)
    return df
