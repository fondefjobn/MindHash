from time import sleep

import numpy as np

from tools.pipes import RoutineSet
from tools.structs import PopList
from tools.visual_utils import vis_utils

"""
@Module: Visualization 
@Description: 
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
    frame: int = 0
    input: PopList
    window: vis_utils.VisUtils

    def __init__(self, in_ls: PopList):
        self.input = in_ls

    def start_visualization(self):
        self.running = True
        self.visualize()

    def stop_visualization(self):
        self.running = False

    def visualize(self):
        while self.running and not self.input.full(self.frame):
            self.wait_for_data()
            self.draw_frame()
            self.frame += 1

    def wait_for_data(self):
        while len(self.input) <= self.frame:
            sleep(0.01)

    def draw_frame(self):
        if self.frame == 0:
            self.window = vis_utils.VisUtils()

        points = self.input[self.frame]['points']
        predictions = self.input[self.frame]['predictions']
        self.window.draw_scenes(
            points=np.asarray(points),
            ref_boxes=np.asarray(predictions['ref_boxes']),
            ref_scores=np.asarray(predictions['ref_scores']),
            ref_labels=np.asarray(predictions['ref_labels'])
        )

