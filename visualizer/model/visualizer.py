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

    def draw_frame(self, points: np.ndarray, predictions: dict = None):
        """

        """
        if predictions is None:
            self.window.draw_scenes(
                points=np.asarray(points))
        else:
            self.window.draw_scenes(
                points=np.asarray(points),
                ref_boxes=np.asarray(predictions['ref_boxes']),
                ref_scores=np.asarray(predictions['ref_scores']),
                ref_labels=np.asarray(predictions['ref_labels'])
            )
