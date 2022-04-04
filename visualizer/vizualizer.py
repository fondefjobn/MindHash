from threading import Event
from time import sleep

import numpy as np

from tools.pipes import RoutineSet
from tools.structs import PopList
from tools.visual_utils import vis_utils

"""
@Module: Visualization 
@Description: Tool for visualizing the pointcloud and the results of the evaluation in 3D
@Author: Bob
"""


class Routines(RoutineSet):

    def id(self):
        return 'VIZ_BUNDLE'

    def Visualization(self, state, *args):
        visualizer = Visualizer(args[0])
        visualizer.start_visualization()


class Visualizer:
    running: bool
    ix: int = 0
    input: PopList
    window: vis_utils.VisUtils
    event: Event = Event()

    def __init__(self, in_ls: PopList):
        self.input = in_ls

    def start_visualization(self):
        self.running = True
        self.visualize()

    def stop_visualization(self):
        self.running = False

    def visualize(self):
        self.window = vis_utils.VisUtils()
        while self.running and not self.input.full(self.ix):
            self.draw_frame()
            self.ix += 1
        self.running = False

    def draw_frame(self):
        frame = self.input.get(self.ix, self.event)
        points = frame['points']
        predictions = frame['predictions']
        self.window.draw_scenes(
            points=np.asarray(points),
            ref_boxes=np.asarray(predictions['ref_boxes']),
            ref_scores=np.asarray(predictions['ref_scores']),
            ref_labels=np.asarray(predictions['ref_labels'])
        )
