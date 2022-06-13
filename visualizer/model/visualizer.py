from threading import Thread
import numpy as np
import time
from visualizer.view import vis_utils
from visualizer.controller import command_handler


class Visualizer(Thread):
    running: bool
    window: vis_utils.VisUtils
    controller: command_handler.CommandHandler
    paused: bool
    points: list
    predictions: list
    frame: int
    fps: int

    def enable(self):
        self.points = [None]
        self.predictions = [None]
        self.frame = 0
        self.paused = False
        self.fps = 120
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
        rendered_frame = self.frame - 1
        while self.running:
            start = time.time()
            self.window.vis.poll_events()
            if self.frame != rendered_frame:
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
                rendered_frame = self.frame

            if not self.paused and self.frame + 1 < len(self.points):
                self.frame += 1
            end = time.time()
            time_elapsed = end - start
            time.sleep(max(1/self.fps - time_elapsed, 0))


