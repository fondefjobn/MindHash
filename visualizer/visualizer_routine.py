from typing import List
from tools.pipes import RNode
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

    @classmethod
    def script(cls, parser) -> bool:
        parser.add_argument('--visual', help='Visualize results with Open3D', action="store_true")
        return True

    def __init__(self, state):
        super().__init__(state)

    def run(self, _input: List[PopList], output: PopList, **kwargs):
        _input[0].get(0, self.event)
        visualizer = Visualizer()
        visualizer.enable()
        x = 0
        while visualizer.running and not _input[0].full(x):
            visualizer.draw_frame(_input[0].get(x, self.event),
                                  _input[1].get(x, self.event))
            x += 1

    def dependencies(self):
        from streamprocessor.stream_process import Routines as processor
        from OpenPCDet.tools.evaluate import Routines as detector
        return [processor, detector]
