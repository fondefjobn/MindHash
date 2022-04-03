from tools.pipes import RoutineSet
from time import sleep
from tools.structs import PopList
import numpy as np
from tools.visual_utils import vis_utils

class Routines(RoutineSet):
    def id(self):
        return 'VIS_BUNDLE'

    def Visualization(self, state, *args):
        visualizer = Visualizer(args[0])
        visualizer.start_visualization()


# REMOVE
pcap_path = "../resources/input/sample/bridge/bridge.pcap"
metadata_path = "../resources/input/sample/bridge/bridge.json"


class Visualizer:
    running: bool
    frame: int = 0
    input: PopList
    window: vis_utils.VisUtils

    def __init__(self, input: PopList):
        self.input = input

    def start_visualization(self):
        self.running = True
        self.visualize()

    def stop_visualization(self):
        self.running = False

    def visualize(self):
        while self.running:
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
