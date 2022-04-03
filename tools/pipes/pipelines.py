import threading
from threading import Thread
from typing import List

from easydict import EasyDict

from tools.structs import PopList
from utilities.utils import FileUtils as fu

"""
@Module: Pipelines
@Description: Simple tool for building and execution of multithreading routines within a chained pipeline
Chaining is achieved with IO PopLists that routines share for parallel list processing. 
See Also Architecture document on Pipelines
@Author: Radu Rebeja
"""

# Dictionary of string values
CONFIG: str = '../tools/pipes/config.yaml'
PRODUCER: str = 'PRODUCER'
CONSUMER: str = 'CONSUMER'
_exec: str = 'exec'
_mt: str = 'mt'


def execute_pipeline(ls_pl: List[Thread]):
    """
    Iterate over all routines and execute all.
    Blocking routines do not use multiprocessing (multithreading)
    Non-Blocking create a separate process with multiprocessing lib
    The state is shared by routines in a list
    A routine uses the state of the previous one which defines current
    state
    Important: Strive for shallow state values (e.g. non-nested dicts, wrapper classes)
    Parameters
    ----------
    ls_pl
    Returns
    -------

    """
    for ix, pl in enumerate(ls_pl):
        pl.start()


def update_routines(bundles: dict, schema: dict, ls_cfg, role: str, pop_ls: PopList):
    """
    v.1
    Initialize missing routines from the list and update Producers and Consumers
    for present instances by assigning either an Input or Output list.
    Parameters
    ----------
    pop_ls
    role
    schema
    bundles
    ls_cfg

    Returns
    -------

    """

    def update(obj_cfg):
        if obj_cfg.ID not in schema:
            if obj_cfg.BUNDLE not in bundles:
                return False
            else:
                schema[obj_cfg.ID] = {
                    _exec: getattr(bundles[obj_cfg.BUNDLE], obj_cfg.ID),
                    PRODUCER: None,
                    CONSUMER: None,
                    _mt: obj_cfg.MT
                }
        schema[obj_cfg.ID][role] = pop_ls
        return True
    list(map(update, ls_cfg))


def build_pipeline(state, bundles) -> List[Thread]:
    """
    Builds pipeline by iterating over the list of PopList dict objects in
    the configuration dictionary. Updates at each step the pipeline chain
    Parameters
    ----------
    bundles list of available bundles
    state shared state containing execution arguments and values
    Returns list of threads (not started)
    -------

    """

    edict = EasyDict(fu.parse_yaml(CONFIG))
    threads: dict = {}
    print(bundles)
    for pls_cfg in edict.PIPELINES.POPLIST:
        pls: PopList = PopList(doc=pls_cfg.ID)
        update_routines(bundles, threads, ls_cfg=pls_cfg.PRODUCER, role=PRODUCER, pop_ls=pls)
        update_routines(bundles, threads, ls_cfg=pls_cfg.CONSUMER, role=CONSUMER, pop_ls=pls)

    pipeline = [threading.Thread(target=r[_exec], args=(state, r[CONSUMER], r[PRODUCER]))
                for r in threads.values()]
    if not pipeline:
        exit(0)
    return pipeline
