from threading import Thread
import numpy as np
import time
from visualizer.view import vis_utils
from visualizer.controller import command_handler
from tools.structs import CachedList

"""
@Module: Visualizer model
@Description: The model of the visualizer that handles the data and passes it to the view. 
It also contains the main loop for drawing the frames.
Points and predictions are added by the visualizer routine, then they are stored
in a cached list.
@Author: Bob van der Vuurst
"""


class Visualizer(Thread):
    running: bool = False
    window: vis_utils.VisUtils
    controller: command_handler.CommandHandler
    paused: bool
    points: CachedList
    predictions: CachedList
    frame: int
    fps: int

    """
    Initialize the cached lists, the view and the controller of the visualizer. 
    """
    def enable(self):
        self.points = CachedList()
        self.points.append(None)
        self.predictions = CachedList()
        self.predictions.append(None)
        self.frame = 0
        self.paused = False
        self.fps = 120
        self.window = vis_utils.VisUtils()
        self.controller = command_handler.CommandHandler(self, self.window.vis)

    """
    Stop the visualizer, close the window for the visualizer.
    """
    def stop(self):
        self.running = False
        self.window.quit()

    """
    Initialize the visualizer, then begin the loop to draw frames.
    """
    def run(self):
        self.enable()
        self.running = True
        self.draw_loop()

    """
    Add points and predictions for one frame to the visualizer, so they can be visualized in the draw loop,
    """
    def add_frame(self, points: np.ndarray, predictions: dict = None):
        self.points.append(np.asarray(points))
        self.predictions.append(predictions)

    """
    The main loop of the visualizer. Each iteration of the loop, it will check for pressed keys,
    execute the commands for those keys and give the frames to the view module for rendering. 
    If the frame is not changed, then the view will not be updated.
    The loop will run at a maximum of self.fps frames per second. 
    """
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

            if not self.paused and self.frame + 1 < min(len(self.points), len(self.predictions)):
                self.frame += 1
            end = time.time()
            time_elapsed = end - start
            time.sleep(max(1/self.fps - time_elapsed, 0))


