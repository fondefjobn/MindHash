from argparse import Namespace
from typing import Dict, Any

from streamprocessor.stream_process import Routines as R_Prc
from sensor.sensor_controller import Routines as Input
from statistic.stats import Routines as R_Stat
from OpenPCDet.tools.evaluate import Routines as R_Eval
from visualizer.vizualizer import Routines as R_Viz
from tools.routines.export import Routines as R_Util


def __generate_list__(args:Namespace) -> Dict[Any, Any]:
    a = args
    __all__ = {(a.live, Input),
               (a.post, Input),
               (True, R_Prc),
               (a.eval, R_Eval),
               (a.visual, R_Viz),
               (a.stats, R_Stat),
               (a.export, R_Util)}

    return dict([(z.id(), z) for z in [y() for (x, y) in __all__ if x is not False]])
