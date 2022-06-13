from typing import List
from tools.pipeline import RNode
from tools.structs import PopList
from visualizer.model.visualizer import Visualizer

"""
@Module: Visualization 
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
        visualizer.enable()
        #visualizer.start()
        while visualizer.running and not _input[0].full(self.ix):
            pts = _input[0].qy(self.ix, self.event)
            det = _input[1].qy(self.ix, self.event) if isinstance(_input[1], PopList) else None
            visualizer.draw_frame(pts, det)
            self.ix += 1

    def dependencies(self):
        from streamprocessor.stream_process import Routines as processor
        from OpenPCDet.tools.detection import Routines as detector
        return [processor, detector]
