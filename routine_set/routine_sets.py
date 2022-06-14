from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from typing import List, Tuple

from OpenPCDet.tools.detection import Routines as R_Detector
from sensor.sensor_controller import Routines as Input
from statistic.stats import Routines as R_Stat
from streamprocessor.stream_process import Routines as R_Prc
from tools.pipeline import RNode
from exports.export import Routines as R_Export
from visualizer.visualizer_routine import Routines as R_Viz
from tools.pipeline.routines import RoutineSet


@dataclass(frozen=True)
class StreetAnalytics(RoutineSet):
    def activationList(self, a: Namespace) -> List[Tuple[object, RNode]]:
        return [(True, Input),
                (True, R_Prc),
                (a.eval, R_Detector),
                (a.visual, R_Viz),
                (a.stats, R_Stat),
                (a.export, R_Export)]

    def __all__(self) -> set:
        return {Input, R_Prc, R_Detector, R_Stat, R_Viz, R_Export}
