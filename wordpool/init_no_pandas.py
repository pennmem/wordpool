def load_no_pandas(words_filepath):
    """Return contents of a word list as a list

    :param str filename: absolute filepath to .data file containing a label line and then words each on a new line.

    :rtype: list

    """

    with open(words_filepath) as words_file:
        words = words_file.read().splitlines()[1:]
    return words

def assign_list_numbers_no_pandas(all_words, number_of_lists, start=0):
    """takes a list of dictionaries with just words and adds listnos.

    :param all_words: a list of dictionaries of all the words to assign numbers to
    :param number_of_lists: how many lists should the words be divided into
    :returns a list of (word, list_number) pairs.

    """
    if ((len(all_words))%number_of_lists != 0):
        raise ValueError("The number of words must be evenly divisible by the number of lists.")
    
    length_of_each_list = len(all_words)/number_of_lists
    for i in range(len(all_words)):
        all_words[i]['listno'] = (i/length_of_each_list) + start
    return all_words
