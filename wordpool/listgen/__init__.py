"""List generation and I/O."""

import random
import os.path as osp
import numpy.random as npr
import pandas as pd

from .. import load, pool_dataframe_to_pool_list, pool_list_to_pool_dataframe, exc
from ..nopandas import assign_list_types_from_type_list, assign_multistim_from_stim_channels_list, extract_blocks
from . import fr, catfr, pal  # noqa

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

        * ``BASELINE``
        * ``PS``
        * ``STIM``
        * ``NON-STIM``

        :param pd.DataFrame pool: Input word pool
        :param int num_baseline: Number of baseline trials
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

    parameters_lists = num_baseline + num_nonstim + num_stim + num_ps
    error_message = "Parameters call for " + str(parameters_lists) + " lists, but I see " + str(len(listnos)) + " list numbers."
    assert len(listnos) == parameters_lists, error_message

    stim_or_nostim = ["NON-STIM"] * num_nonstim + ["STIM"] * num_stim
    random.shuffle(stim_or_nostim)

    pool_list = pool_dataframe_to_pool_list(pool)
    pool_list = assign_list_types_from_type_list(pool_list, num_baseline, stim_or_nostim, num_ps=num_ps)
    pool_dataframe = pool_list_to_pool_dataframe(pool_list)

    return pool_dataframe


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
    assert 'phase_type' in pool.columns, "You must assign stim lists first"
    assert 'STIM' in pool['phase_type'].unique(), "You must assign stim lists first"
    stim_lists = list(pool[pool['phase_type'] == 'STIM'].listno.unique())
    assert sum(stimspec.values()) == len(stim_lists), \
        "Incompatible number of stim lists"

    stimspec_list = []
    for key, value in stimspec.items():
        stimspec_list += [key] * value
    random.shuffle(stimspec_list)

    pool_list = pool_dataframe_to_pool_list(pool)
    pool_list = assign_multistim_from_stim_channels_list(pool_list, stimspec_list)
    pool_dataframe = pool_list_to_pool_dataframe(pool_list)

    return pool_dataframe


def generate_rec1_blocks(pool, lures):
    """Generate REC1 word blocks.

        :param pd.DataFrame pool: Word pool used in verbal task session.
        :param pd.DataFrame lures: Lures to use.
        :returns: :class:`pd.DataFrame`.

        """
    # Remove practice and baseline lists
    allowed = pool[~pool.isin(["PRACTICE", "BASELINE"])]

    # Divide into stim lists (exclude if in last four)...
    stims = allowed[(allowed.phase_type == "STIM") & (allowed.listno <= allowed.listno.max() - 4)]

    # ...and nonstim lists (take all)
    nonstims = allowed[allowed.phase_type == "NON-STIM"]

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


def generate_learn1_blocks(pool, num_nonstim, num_stim, stim_channels=(0, 1), num_blocks=4):
    """Generate blocks for the LEARN1 (repeated list learning) subtask.

        :param pd.DataFrame pool: Input word pool.
        :param int num_nonstim: Number of nonstim lists to include.
        :param int num_stim: Number of stim lists to include.
        :param tuple stim_channels: Tuple of stim channels to draw from.
        :returns: 4 blocks of lists as a :class:`pd.DataFrame`.

        """
    nonstim_listnos = random.sample(list(pool[pool.phase_type == 'NON-STIM'].listno.unique()), num_nonstim)
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
