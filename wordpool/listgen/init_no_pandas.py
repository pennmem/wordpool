def assign_list_types_no_pandas(pool, num_baseline, stim_nonstim, num_ps=0):
    """Assign list types to a pool. The types are:
        
        * ``PRACTICE``
        * ``BASELINE``
        * ``PS``
        * ``STIM``
        * ``NON-STIM``
        
        :param pd.DataFrame pool: Input word pool.  list of (word, listno) pairs
        :param int num_baseline: Number of baseline trials *excluding* the practice
        list.
        :param list stim_nonstim: a list of "STIM" or "NON-STIM" strings indicating the order of stim and non-stim interleaved lists.
        :param int num_ps: Number of parameter search trials.
        :returns: pool with assigned types
        :rtype: list
        
        """
    
    # Check that the inputs match the number of lists
    last_listno = pool[-1][1]
    assert last_listno == num_baseline + len(stim_nonstim) + num_ps, "The number of lists and provided type parameters didn't match"
    
    
    for i in range(len(pool)):
        word = pool[i]
        if (word[1] == 0):
            pool[i] = (word[0], word[1], None, "PRACTICE")
        elif (word[1] <= num_baseline):
            pool[i] = (word[0], word[1], None, "BASELINE")
        elif (word[1] <= num_baseline + num_ps):
            pool[i] = (word[0], word[1], None, "PS")
        else:
            stimtype = stim_nonstim[word[1]-num_ps-num_baseline-1]
            pool[i] = (word[0], word[1], (0,), stimtype) if (stimtype == "STIM") else (word[0], word[1], None, stimtype)

    return pool


def assign_multistim_no_pandas(pool, stimspec_list):
    """Update stim lists to account for multiple stimulation sites.
        
        
        :param list pool: Word pool with assigned stim lists. (word, listno, stim_channels, type)
        :param list names: Names of individual stim channels.
        :rtype: list
        
        """
    assert len(pool) > 0, "Empty pool"
    assert len(pool[0]) == 4, "Pool should be a list of four-tuples"
    
    stim_words = [word for word in pool if word[3] == "STIM"]
    unique_listnos = set()
    for word in stim_words:
        unique_listnos.add(word[1])

    assert len(unique_listnos) == len(stimspec_list), "The number of stimspecs should be the same as the number of stim lists."

    current_stimspec_index = -1
    stim_listno = -1
    for i in range(len(pool)):
        word = pool[i]
        if (word[3] == "STIM"):
            if (word[1] != stim_listno):
                stim_listno = word[1]
                current_stimspec_index += 1
            pool[i] = (word[0], word[1], stimspec_list[current_stimspec_index], word[3])


    return pool


