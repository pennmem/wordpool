import numpy as np
import pandas as pd
from .nopandas import assign_list_numbers_from_word_list
from pkg_resources import resource_filename, resource_listdir

__version__ = "0.5.dev0"


def list_available_pools():
    """Returns a list of the pools available in the `wordpool.data` package."""
    files = resource_listdir("wordpool", "data")
    return [f for f in files if f.endswith(".txt")]


def load(filename, from_data_package=True):
    """Return contents of a word list.

    :param str filename:
    :param bool from_data_package: When True (the default), load data from the
        ``wordpool.data`` package. Otherwise, treat the filename as an absolute
        path to load arbitrary wordpools from.
    :rtype: pd.DataFrame

    """
    if from_data_package:
        src = resource_filename("wordpool.data", filename)
    else:
        src = filename
    return pd.read_table(src)


def assign_list_numbers(df, n_lists, start=0):
    """Assign or reassign list numbers to all words in the pool.

    :param pd.DataFrame df: Input word pool
    :param int n_lists: Total number of lists.
    :param int start: Start number for lists.
    :returns: Word pool with list numbers assigned

    """
    assert len(df) % n_lists == 0
    
    pool_list = pool_dataframe_to_pool_list(df)
    pool_list = assign_list_numbers_from_word_list(pool_list, n_lists, start=start)
    df = pool_list_to_pool_dataframe(pool_list)

    return df


def pool_dataframe_to_pool_list(pool_dataframe):
    """Covert a panda dataframe to a list of dictionaries.  For datafroms with word1 and word2 columns, make those a single tuple under the key 'word'.
        
    """
    if 'word1' in pool_dataframe.columns and 'word2' in pool_dataframe.columns:
        word_pairs = pool_dataframe[['word1', 'word2']].values
        del pool_dataframe['word1']
        del pool_dataframe['word2']
        pool_dataframe.insert(0, 'word', [tuple(pair) for pair in word_pairs])

    pool_list = [{} for i in range(len(pool_dataframe))]
    for column, values in pool_dataframe.iteritems():
        for i in range(len(values)):
            pool_list[i][column] = values[i]

    return pool_list


def pool_list_to_pool_dataframe(pool_list):
    """Covert a list of dictionaries to a panda dataframe.  For dictionaries with a 'word' entry that is a pair, convert that to two seperate columns called 'word1' and 'word2'
        
    """
    pool_dataframe = pd.DataFrame()
    if len(pool_list) == 0:
        return pool_dataframe
    
    for key in pool_list[0].keys():
        pool_dataframe[key] = [word[key] for word in pool_list]

    if ('word' in pool_dataframe) and (type(pool_dataframe['word'][0]) == tuple) and (len(pool_dataframe['word'][0]) == 2):
        word_pairs = pool_dataframe['word']
        pool_dataframe['word1'] = [pair[0] for pair in word_pairs]
        pool_dataframe['word2'] = [pair[1] for pair in word_pairs]

    return pool_dataframe


def shuffle_words(df):
    """Shuffle words.

    :param pd.DataFrame df: Input word pool
    :returns: Shuffled pool

    """
    shuffled = df.reindex(np.random.permutation(df.index))
    return shuffled.reset_index(drop=True)


def shuffle_within_groups(df, column):
    """Shuffle within groups of words based on some common values in a column.

    :param pd.DataFrame df: Input word pool
    :param str column: Column name.
    :returns: Pool with groups shuffled.

    """
    if column not in df.columns:
        raise RuntimeError("Column {} not found in DataFrame".format(column))

    shuffled = []
    for col in df[column].unique():
        list_ = df[df[column] == col]
        shuffled.append(list_.reindex(np.random.permutation(list_.index)))

    return pd.concat(shuffled).reset_index(drop=True)


def shuffle_within_lists(df):
    """Shuffle within lists in the pool (i.e., shuffle each list but do not
    move any words between lists. This requires that list
    numbers have alreay been assigned.

    :param pd.DataFrame df: Input word pool
    :returns: Pool with lists shuffled

    """
    if "listno" not in df.columns:
        raise RuntimeError("You must assign list numbers first.")

    return shuffle_within_groups(df, "listno")
