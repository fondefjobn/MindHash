from argparse import Namespace
from dataclasses import dataclass
from typing import Dict, Set

from OpenPCDet.tools.evaluate import Routines as R_Eval
from sensor.sensor_controller import Routines as Input
from statistic.stats import Routines as R_Stat
from streamprocessor.stream_process import Routines as R_Prc
from tools.pipes import RNode
from tools.routines.export import Routines as R_Export
from visualizer.visualizer import Routines as R_Viz

"""
    Generates ordered list of all routines that may be part of the pipeline
    Tuple associates a key from CLI argparse with a routine
    If a routine existence is required, use anything as key except None

    Dict[Arg/Any | Routine]
"""


@dataclass(frozen=True)
class RoutineSet:
    __all__ = {Input, R_Prc, R_Eval, R_Stat, R_Viz, R_Export}


def __generate_list__(state, args: Namespace) -> Dict[int, RNode]:
    a = args
    __all__ = [(True, Input),
               (True, R_Prc),
               (a.eval, R_Eval),
               (a.visual, R_Viz),
               (a.stats, R_Stat),
               (a.export, R_Export)]
    return dict([(hash(y), y(state)) for (x, y) in __all__ if x is not (False and None)])
