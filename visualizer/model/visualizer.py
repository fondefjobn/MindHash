import threading
import numpy as np
from visualizer.view import vis_utils
from visualizer.controller import command_handler


class Visualizer(threading.Thread):
    running: bool
    window: vis_utils.VisUtils
    controller: command_handler.CommandHandler
    paused: bool
    points: list
    predictions: list
    frame: int

    def enable(self):
        self.points = [None]
        self.predictions = [None]
        self.frame = 0
        self.paused = False
        self.window = vis_utils.VisUtils()
        self.controller = command_handler.CommandHandler(self, self.window.vis)

    def stop(self):
        self.running = False
        self.window.quit()

    def run(self):
        self.running = True
        self.enable()
        self.draw_loop()

    def add_frame(self, points: np.ndarray, predictions: dict = None):
        self.points.append(np.asarray(points))
        self.predictions.append(predictions)

    def draw_loop(self):
        while self.running:
            if not self.paused and self.frame < len(self.points):
                if self.predictions[self.frame] is None:
                    self.window.draw_scenes(
                        points=self.points[self.frame])
                else:
                    self.window.draw_scenes(
                        points=self.points[self.frame],
                        ref_boxes=np.asarray(self.predictions[self.frame]['ref_boxes']),
                        ref_scores=np.asarray(self.predictions[self.frame]['ref_scores']),
                        ref_labels=np.asarray(self.predictions[self.frame]['ref_labels'])
                    )
                self.frame += 1
            else:
                self.window.vis.poll_events()

