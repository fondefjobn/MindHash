import numpy as np
from visualizer.view import vis_utils


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
            ref_boxes=predictions['ref_boxes'],
            ref_scores=predictions['ref_scores'],
            ref_labels=predictions['ref_labels']
        )

