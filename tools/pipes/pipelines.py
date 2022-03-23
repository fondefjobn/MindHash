from abc import ABC

from typing import List, Tuple

from StreamProcessor.stream_process import QueueProcessor
from tools.evaluate import Evaluate
from tools.pipes.p_tmpl import Pipeline, State, GlobalDictionary as Gd
from sensor.sensor_controller import LiveStream
from statistics.stats import Statistics
from utilities.utils import PcapProcess, ExportLocal
from visualizer.viz_module import Visualization

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
"""


def __generate_list__(args) -> List[Tuple[str, Pipeline]]:
    a = args
    __all__: List[Tuple[str, Pipeline]] = [
        (a.live, LiveStream),
        (a.post, PcapProcess),
        (True, QueueProcessor),
        (a.eval, Evaluate),
        (a.visual, Visualization),
        (a.stats, Statistics),
        (a.export, ExportLocal)
    ]
    return __all__


def execute_pipeline(ls_pl: List[Pipeline]):
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
    init = ls_pl[0]
    init.execute(init.state)
    for ix, pl in enumerate(ls_pl[1:]):
        pl.execute(ls_pl[ix - 1].state)
        print(pl.state[Gd.Success], pl.state[Gd.Step])


def build_pipeline(args) -> List[Pipeline]:
    state: State = State()
    state.args = args
    pipeline: List[Pipeline] = []
    for (key, pline) in __generate_list__(args):
        if key is not None:
            pipeline.append(pline())
    if pipeline:
        pipeline[0].state = state
    else:
        exit(0)
    return pipeline
