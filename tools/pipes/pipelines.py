import threading
from threading import Thread
from typing import List, Any, Dict

from easydict import EasyDict

from StreamProcessor.stream_process import Routines as R_Prc
from sensor.sensor_controller import Routines as R_Live
from statistics.stats import Routines as R_Stat
from tools.evaluate import Routines as R_Eval
from tools.pipes.p_template import State
from utilities.custom_structs import PopList
from utilities.utils import Routines as R_Util, FileUtils as fu
from visualizer.viz_module import Routines as R_Viz

"""
Tool module for building pipeline execution of functions
Idea: The behavior of the execution is split in modules.
Module execution input arguments vary, how to chain execution safe & clean?
Solution: Sequential execution of separate routines sharing one state
"""

"""
    Generates ordered list of all routines that may be part of the pipeline
    Tuple associates a key from CLI argparse with a routine
    If a routine existence is required, use anything as key except None
    Arg/Any | Routine | isThreaded
"""

CONFIG: str = '../tools/pipes/config.yaml'


def __generate_list__(args) -> Dict[Any, Any]:
    a = args
    __all__ = {(a.live, R_Live),
               (a.post, R_Util),
               (True, R_Prc),
               (a.eval, R_Eval),
               (a.visual, R_Viz),
               (a.stats, R_Stat),
               (a.export, R_Util)}

    return dict([(y.id(), y) for y in [y() for (x, y) in __all__ if x is not None]])


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
        # print(pl.state[id(Gd.Success)], pl.state[id(Gd.Step)])


def update_routines(bundles: dict, schema: dict, ls_cfg, role: str, pop_ls: list):
    """

    Parameters
    ----------
    pop_ls
    role
    schema
    bundles
    r_id
    ls_cfg
    producer

    Returns
    -------

    """

    def update(obj_cfg):
        if obj_cfg.ID not in schema:
            if obj_cfg.BUNDLE not in bundles:
                return False
            else:
                schema[obj_cfg.ID] = {
                    'exec': getattr(bundles[obj_cfg.BUNDLE], obj_cfg.ID),
                    'PRODUCER': None,
                    'CONSUMER': None,
                    'mt': obj_cfg.MT
                }
        schema[obj_cfg.ID][role] = pop_ls
        return True
    list(map(update, ls_cfg))


def build_pipeline(args) -> List:
    """

    Parameters
    ----------
    args

    Returns
    -------

    """
    state: State = State(args)
    pipeline: List[Thread] = []

    edict = EasyDict(fu.parse_yaml(CONFIG))

    print(edict)
    bundles = __generate_list__(args)
    thrds: dict = {}
    print(bundles)
    for pls_cfg in edict.PIPELINES.POPLIST:
        pls: PopList = PopList(doc=pls_cfg.ID)
        update_routines(bundles, thrds, ls_cfg=pls_cfg.PRODUCER, role='PRODUCER', pop_ls=pls)
        update_routines(bundles, thrds, ls_cfg=pls_cfg.CONSUMER, role='CONSUMER', pop_ls=pls)

    print('-----------------',thrds.items())
    pipeline = [threading.Thread(target=r["exec"], args=(state, r["CONSUMER"], r["PRODUCER"])) for r in thrds.values()
                if r["mt"] is True]
    print(pipeline)
    if not pipeline:
        exit(0)
    return pipeline
