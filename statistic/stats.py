from typing import List, Tuple

from tools.pipes import RNode
from tools.structs import PopList


class Routines(RNode):
    """
    Statistic routine
    """

    @classmethod
    def script(cls, parser):
        parser.add_argument('--stats', help='Generate statistic', action="store_true")

    def __init__(self, state):
        super().__init__(state)

    def run(self, _input: List[PopList], output: PopList, **kwargs):
        pass

    def dependencies(self):
        from streamprocessor.stream_process import Routines as processor
        from OpenPCDet.tools.evaluate import Routines as detectors
        return [processor, detectors]
