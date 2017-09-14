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
    last_listno = pool[-1]['listno']
    assert last_listno == num_baseline + len(stim_nonstim) + num_ps, "The number of lists and provided type parameters didn't match"
    
    
    for i in range(len(pool)):
        word = pool[i]
        if (word['listno'] == 0):
            pool[i]['type'] = "PRACTICE"
            pool[i]['stim_channels'] = None
        elif (word['listno'] <= num_baseline):
            pool[i]['type'] = "BASELINE"
            pool[i]['stim_channels'] = None
        elif (word['listno'] <= num_baseline + num_ps):
            pool[i]['type'] = "PS"
            pool[i]['stim_channels'] = None
        else:
            stimtype = stim_nonstim[word['listno']-num_ps-num_baseline-1]
            pool[i]['type'] = stimtype
            pool[i]['stim_channels'] = (0,) if stimtype == "STIM" else None

    return pool


def assign_multistim_no_pandas(pool, stimspec_list):
    """Update stim lists to account for multiple stimulation sites.
        
        
        :param list pool: Word pool with assigned stim lists. (word, listno, stim_channels, type)
        :param list names: Names of individual stim channels.
        :rtype: list
        
        """
    assert len(pool) > 0, "Empty pool"
    assert len(pool[0]) == 4, "Pool should be a list of four-tuples"
    
    stim_words = [word for word in pool if word['type'] == "STIM"]
    unique_listnos = set()
    for word in stim_words:
        unique_listnos.add(word['listno'])

    assert len(unique_listnos) == len(stimspec_list), "The number of stimspecs should be the same as the number of stim lists."

    current_stimspec_index = -1
    stim_listno = -1
    for i in range(len(pool)):
        word = pool[i]
        if (word['type'] == "STIM"):
            if (word['listno'] != stim_listno):
                stim_listno = word['listno']
                current_stimspec_index += 1
            pool[i]['stim_channels'] = stimspec_list[current_stimspec_index]


    return pool



def extract_blocks(pool, listnos, num_blocks):
    """Take out lists based on listnos and separate them into blocks
        
        :param list pool: Input word pool.
        :param list listnos: The order of lists to separate into blocks
        :param int num_blocks: The number of blocks to organize the listnos into
        :returns: blocks of words as a list of tuples
        
        """
    assert len(listnos)%num_blocks == 0, "The number of lists to append must be divisable by the number of blocks"
    
    wordlists = {}
    for word in pool:
        wordlists[word['listno']] = wordlists.get(word['listno'], []) + [word]
    
    blocks = []
    for i in range(len(listnos)):
        listno = listnos[i]
        wordlist = [word.copy() for word in wordlists[listno]]
        for word in wordlist:
            word['blockno'] = i/num_blocks
        blocks += wordlist

    return blocks

