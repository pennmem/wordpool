"""List generation and I/O."""

try:
    import random
except:
    random = None
try:
    import os.path as osp
except:
    osp = None
try:
    import itertools
except:
    itertools = None
try:
    import numpy.random as npr
except:
    npr = None
try:
    import pandas as pd
except:
    pd = None

try:
    from .. import load, pool_dataframe_to_pool_list, pool_list_to_pool_dataframe, exc
except ImportError:
    load = pool_dataframe_to_pool_list = pool_list_to_pool_dataframe = exc = None
try:
    from . import fr, catfr, pal
except ImportError:
    fr = catfr = pal = None

if (load):
    RAM_LIST_EN = load("ram_wordpool_en.txt")
    RAM_LIST_SP = load("ram_wordpool_sp.txt")

    CAT_LIST_EN = load("ram_categorized_en.txt")
    CAT_LIST_SP = load("ram_categorized_sp.txt")

    PRACTICE_LIST_EN = load("practice_en.txt")
    PRACTICE_LIST_SP = load("practice_sp.txt")

    LURES_LIST_EN = load("REC1_lures_en.txt")


def write_wordpool_txt(path, language="EN", include_lure_words=False,
                       categorized=False):
    """Write `RAM_wordpool.txt` or `CatFR_WORDS.txt` to a file (why the naming
        is so inconsistent is beyond me). This is used in event post-processing.
        
        :param str path: Directory to write file to.
        :param str language: Language to use ("EN" or "SP").
        :param bool include_lure_words: Also write lure words to ``path``.
        :param bool categorized: When True, write the categorized word pool.
        :returns: list of filenames written
        
        """
    if language not in ["EN", "SP"]:
        raise exc.LanguageError("Invalid language specified")
    if language == "SP" and include_lure_words:
        raise exc.LanguageError("Spanish lure words don't exist yet")
    
    kwargs = {
        "index": False,
        "header": False,
        "encoding": "utf8"
    }
    
    if categorized:
        words = CAT_LIST_EN if language == "EN" else CAT_LIST_SP
        filename = osp.join(path, "CatFR_WORDS.txt")
    else:
        words = RAM_LIST_EN if language == "EN" else RAM_LIST_SP
        filename = osp.join(path, "RAM_wordpool.txt")
    ret = [filename]
    words.word.to_csv(filename, **kwargs)

    if include_lure_words:
        lures = LURES_LIST_EN
        filename = osp.join(path, "RAM_lurepool.txt")
        lures.to_csv(filename, **kwargs)
        ret.append(filename)
    
    return ret


def assign_list_types(pool, num_baseline, num_nonstim, num_stim, num_ps=0):
    """Assign list types to a pool. The types are:
        
        * ``PRACTICE``
        * ``BASELINE``
        * ``PS``
        * ``STIM``
        * ``NON-STIM``
        
        :param pd.DataFrame pool: Input word pool
        :param int num_baseline: Number of baseline trials *excluding* the practice
        list.
        :param int num_nonstim: Number of non-stim trials.
        :param int num_stim: Number of stim trials.
        :param int num_ps: Number of parameter search trials.
        :returns: pool with assigned types
        :rtype: pd.DataFrame
        
        """
    # List numbers should already be assigned and sorted
    listnos = pool.listno.unique()
    assert all([n == m for n, m in zip(listnos, sorted(listnos))])
    
    # Check that the inputs match the number of lists
    assert len(listnos) == num_baseline + num_nonstim + num_stim + num_ps + 1
    
    stim_or_nostim = ["NON-STIM"] * num_nonstim + ["STIM"] * num_stim
    random.shuffle(stim_or_nostim)
    
    
    pool_list = pool_dataframe_to_pool_list(pool)
    pool_list = assign_list_types_from_type_list(pool_list, num_baseline, stim_or_nostim, num_ps = num_ps)
    pool_dataframe = pool_list_to_pool_dataframe(pool_list)
    
    return pool_dataframe

def assign_list_types_from_type_list(pool, num_baseline, stim_nonstim, num_ps=0):
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
    assert 'type' in pool.columns, "You must assign stim lists first"
    assert 'STIM' in pool['type'].unique(), "You must assign stim lists first"
    stim_lists = list(pool[pool['type'] == 'STIM'].listno.unique())
    assert sum(stimspec.values()) == len(stim_lists), \
        "Incompatible number of stim lists"
    
    stimspec_list = []
    for key, value in stimspec.iteritems():
        stimspec_list += [key] * value
    random.shuffle(stimspec_list)
    
    pool_list = pool_dataframe_to_pool_list(pool)
    pool_list = assign_multistim_from_stim_channels_list(pool_list, stimspec_list)
    pool_dataframe = pool_list_to_pool_dataframe(pool_list)
    
    return pool_dataframe

def assign_multistim_from_stim_channels_list(pool, stimspec_list):
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




def generate_rec1_blocks(pool, lures):
    """Generate REC1 word blocks.
        
        :param pd.DataFrame pool: Word pool used in verbal task session.
        :param pd.DataFrame lures: Lures to use.
        :returns: :class:`pd.DataFrame`.
        
        """
    # Remove practice and baseline lists
    allowed = pool[~pool.isin(["PRACTICE", "BASELINE"])]
    
    # Divide into stim lists (exclude if in last four)...
    stims = allowed[(allowed.type == "STIM") & (allowed.listno <= allowed.listno.max() - 4)]
    
    # ...and nonstim lists (take all)
    nonstims = allowed[allowed.type == "NON-STIM"]
    
    # Randomly select stim list numbers
    stim_idx = pd.Series(stims.listno.unique()).sample(6)
    rec_stims = stims[stims.listno.isin(stim_idx)]
    rec_nonstims = nonstims
    
    # Combine selected words
    targets = pd.concat([rec_stims, rec_nonstims])
    
    # Give lures list numbers
    lures["type"] = "LURE"
    lures["listno"] = npr.choice(targets.listno.unique(), len(lures))
    
    # Set default category values if this is catFR
    if "category" in pool.columns:
        lures["category"] = "X"
        lures["category_num"] = -999
    
    # Combine lures and targets
    combined = pd.concat([targets, lures]).sort_values(by="listno")
    listnos = combined.listno.unique()

    # Break into two blocks and shuffle
    block_listnos = [listnos[:int(len(listnos)/2)], listnos[int(len(listnos)/2):]]
    blocks = [combined[combined.listno.isin(idx)].sample(frac=1) for idx in block_listnos]
    return pd.concat(blocks).reset_index()


def generate_learn1_blocks(pool, num_nonstim, num_stim, stim_channels=(0,1), num_blocks=4):
    """Generate blocks for the LEARN1 (repeated list learning) subtask.
        
        :param pd.DataFrame pool: Input word pool.
        :param int num_nonstim: Number of nonstim lists to include.
        :param int num_stim: Number of stim lists to include.
        :param tuple stim_channels: Tuple of stim channels to draw from.
        :returns: 4 blocks of lists as a :class:`pd.DataFrame`.
        
        """
    nonstim_listnos = random.sample(list(pool[pool.type == 'NON-STIM'].listno.unique()), num_nonstim)
    stim_listnos = random.sample(list(pool[pool.stim_channels == stim_channels].listno.unique()), num_stim)
    listnos = nonstim_listnos + stim_listnos
    
    listnos_sequence = []
    for i in range(num_blocks):
        block_listnos = listnos[:]
        random.shuffle(block_listnos)
        listnos_sequence += block_listnos
    
    pool_list = pool_dataframe_to_pool_list(pool)
    result_list = extract_blocks(pool_list, listnos_sequence, num_blocks)
    result = pool_list_to_pool_dataframe(result_list)

    return result



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
            word['block_listno'] = i
        blocks += wordlist
    
    return blocks
