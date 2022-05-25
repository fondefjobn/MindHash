import threading
import open3d.visualization.gui as gui
import numpy as np
from visualizer.view import vis_utils, window
import time

FRAMES_PER_SECOND = 20


class Visualizer(threading.Thread):
    running: bool
    window: window.Window
    current_frame: int
    paused: bool
    points: list
    predictions: list
    fps: int
    thread: threading.Thread

    def __init__(self):
        super().__init__()
        self.window = None
        self.current_frame = 0
        self.paused = False  # TODO: change to false
        self.points = []
        self.predictions = []
        self.fps = FRAMES_PER_SECOND

    def run(self):
        self.running = True
        self.start_window()

        self.draw_loop()

    def enable(self):

        time.sleep(2)  # FIXME

#        self.window = vis_utils.VisUtils()
        self.running = True

        self.start_loop()

    def start_window(self):
        self.window = window.Window()
        self.window.start()

    def stop(self):
        self.running = False

    def draw_frame(self, points: np.ndarray, predictions: dict):
        self.window.draw_scenes(
            points=np.asarray(points),
            ref_boxes=np.asarray(predictions['ref_boxes']),
            ref_scores=np.asarray(predictions['ref_scores']),
            ref_labels=np.asarray(predictions['ref_labels'])
        )

    def add_frame(self, points: np.ndarray, predictions: dict): #FIXME: ugly, not thread safe
        self.points.append(points)
        self.predictions.append(predictions)

    def draw_loop(self):
        while self.running and self.window.running:
            start = time.time()
            if not self.paused and self.window.has_initialized and self.current_frame < len(self.points):  # FIXME
                print(f"Visualizer: frame {self.current_frame}")
                self.window.draw_scenes(
                    points=np.asarray(self.points[self.current_frame]),
                    ref_boxes=np.asarray(self.predictions[self.current_frame]['ref_boxes']),
                    ref_scores=np.asarray(self.predictions[self.current_frame]['ref_scores']),
                    ref_labels=np.asarray(self.predictions[self.current_frame]['ref_labels'])
                )
                self.current_frame += 1
            end = time.time()
            if self.fps != 0:
                time.sleep(max(1/self.fps - (end-start), 0))  # FIXME: alternative for time.sleep

