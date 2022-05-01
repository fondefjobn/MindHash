from typing import List, Tuple

import numpy as np

from tools.pipes import RNode
from tools.structs import PopList
from tools.visual_utils import vis_utils

"""
@Module: Visualization 
@Description: Tool for visualizing the pointcloud and the results of the evaluation in 3D
@Author: Bob
"""


class Visualizer:
    running: bool
    window: vis_utils.VisUtils

    def enable(self):
        self.window = vis_utils.VisUtils()
        self.running = True

    def stop(self):
        self.running = False

    def draw_frame(self, points: np.ndarray, predictions: dict):
        """

        """
        self.window.draw_scenes(
            points=np.asarray(points),
            ref_boxes=np.asarray(predictions['ref_boxes']),
            ref_scores=np.asarray(predictions['ref_scores']),
            ref_labels=np.asarray(predictions['ref_labels'])
        )


class Routines(RNode):
    """
    Visualisation routine
    """

    @classmethod
    def script(cls, parser) ->bool:
        return False

    def __init__(self, state):
        super().__init__(state)

    def run(self, _input: List[PopList], output: PopList, **kwargs):
        visualizer = Visualizer()
        visualizer.enable()
        x = 0
        while visualizer.running and not _input[0].full(x):
            visualizer.draw_frame(_input[0].get(x, self.event),
                                  _input[1].get(x, self.event))
            x += 1
        visualizer.stop()

    def dependencies(self):
        from streamprocessor.stream_process import Routines as processor
        from OpenPCDet.tools.evaluate import Routines as detector
        return [processor, detector]
