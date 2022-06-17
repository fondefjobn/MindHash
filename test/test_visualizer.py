import unittest
import visualizer
from time import sleep
import numpy as np


class TestVisualizer(unittest.TestCase):
    vis: visualizer.Visualizer

    def initialize_visualizer(self):
        self.vis = visualizer.Visualizer()
        self.vis.start()
        sleep(1)

    def add_frames(self, num_frames, points_per_frame):
        rand_range = 50
        for i in range(num_frames):
            self.vis.add_frame(np.random.rand(points_per_frame, 5) * rand_range - 0.5 * rand_range)

    def test_visualizer(self):
        self.initialize_visualizer()
        self.assertEqual(self.vis.running, True)
        self.vis.stop()
        self.assertEqual(self.vis.running, False)

    def test_commands(self):
        num_frames = 10
        points_per_frame = 5000

        self.initialize_visualizer()
        self.add_frames(num_frames, points_per_frame)
        vis = self.vis
        controller = vis.controller
        self.assertEqual(vis.paused, False)
        controller.toggle_pause(None)
        self.assertEqual(vis.paused, True)
        controller.toggle_pause(None)
        self.assertEqual(vis.paused, False)

        for i in range(num_frames):
            controller.previous_frame(None)
        self.assertEqual(vis.paused, True)
        self.assertEqual(vis.frame, 0)

        controller.next_frame(None)
        self.assertEqual(vis.frame, 1)
        self.assertEqual(vis.paused, True)

        controller.quit(None)
        self.assertEqual(vis.running, False)


if __name__ == '__main__':
    unittest.main()
