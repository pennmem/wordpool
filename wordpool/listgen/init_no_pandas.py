
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
            pool[i] = (word[0], word[1], None, float('nan'))
        elif (word[1] <= num_baseline):
            pool[i] = (word[0], word[1], None, "BASELINE")
        elif (word[1] <= num_baseline + num_ps):
            pool[i] = (word[0], word[1], None, "PS")
        else:
            stimtype = stim_nonstim[word[1]-num_ps-num_baseline-1]
            pool[i] = (word[0], word[1], (0,), stimtype) if (stimtype == "STIM") else (word[0], word[1], None, stimtype)

    return pool


def assign_multistim(pool, stimspec):
    """Update stim lists to account for multiple stimulation sites.
        
        To specify the number of stim lists, use a dict such as::
        
        stimspec = {
        (0,): 5,
        (1,): 5,
        (0, 1): 1
        }
        
        This indicates to use 5 stim lists for site 0, 5 for site 1, and 1 for
        sites 0 and 1. In reality, any string key is acceptable and it is up to the
        stimulator to interpret what they mean.
        
        :param pd.DataFrame pool: Word pool with assigned stim lists.
        :param list names: Names of individual stim channels.
        :param dict stimspec: Stim specifications.
        :returns: Re-assigned word pool.
        :rtype: pd.DataFrame
        
        """
    assert 'STIM' in pool['type'].unique(), "You must assign stim lists first"
    stim_lists = list(pool[pool['type'] == 'STIM'].listno.unique())
    assert sum(stimspec.values()) == len(stim_lists), \
        "Incompatible number of stim lists"
    
    pool['stim_channels'] = None
    for channels, count in stimspec.items():
        assert isinstance(channels, tuple), "stimspec keys must be tuples"
        listnos = []
        for _ in range(count):
            listno = random.choice(stim_lists)
            listnos.append(listno)
            stim_lists.remove(listno)
            pool.loc[pool.listno == listno, 'stim_channels'] = pool.stim_channels.apply(lambda _: channels)

    return pool

