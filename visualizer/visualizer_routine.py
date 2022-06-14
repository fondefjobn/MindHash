from typing import List
from tools.pipeline import RNode
from tools.structs import PopList
from visualizer.model.visualizer import Visualizer

"""
@Module: Visualization Routine
@Description: Tool for visualizing the point cloud and the results of the evaluation in 3D
@Author: Bob van der Vuurst
"""


class Routines(RNode):
    """
    Visualisation routine
    """
    ix: int = 0

    def get_index(self) -> int:
        return self.ix

    @classmethod
    def script(cls, parser) -> bool:
        parser.add_argument('--visual', help='Visualize results with Open3D', action="store_true")
        return True

    def __init__(self, state):
        super().__init__(state)

    @RNode.assist
    def run(self, _input: List[PopList], output: PopList, **kwargs):
        _input[0].qy(0, self.event)
        visualizer = Visualizer()
        visualizer.start()
        if isinstance(_input[1], PopList):
            while not _input[0].full(self.ix):
                visualizer.add_frame(_input[0].qy(self.ix, self.event),
                                     _input[1].qy(self.ix, self.event))
                self.ix += 1
        else:
            while not _input[0].full(self.ix):
                visualizer.add_frame(_input[0].qy(self.ix, self.event),
                                     None)
                self.ix += 1

    def dependencies(self):
        from streamprocessor.stream_process import Routines as processor
        from OpenPCDet.tools.detection import Routines as detector
        return [processor, detector]
