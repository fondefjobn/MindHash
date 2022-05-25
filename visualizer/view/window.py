import threading
import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
import numpy as np

# TODO: This should all be in the config file
WINDOW_NAME = "Mindhash Visualizer"
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
SCENE_WIDTH = 1600
SCENE_HEIGHT = 900
SCENE_BACKGROUND_COLOR = [0, 0, 0, 1]
THIRD_PERSON_VIEW = {
    "center": np.array([0, 0, 0]),
    "eye": np.array([-10, 0, 5]),
    "up": np.array([0, 0, 1])
}
BIRDS_EYE_VIEW = {
    "center": np.array([0, 0, 0]),
    "eye": np.array([0, 0, 20]),
    "up": np.array([1, 0, 0])
}
MATERIAL_POINT_SIZE = 0.5
MATERIAL_SHADER = "defaultUnlit"


class Media:
    scene_widget: gui.SceneWidget
    scene: rendering.Scene
    material: rendering.MaterialRecord

    def __init__(self, renderer):
        self.scene_widget = gui.SceneWidget()

        self.scene = rendering.Open3DScene(renderer)
        self.scene_widget.scene = self.scene
        self.scene_widget.frame = gui.Rect(0, 0, SCENE_WIDTH, SCENE_HEIGHT)
        self.setup_material()
        self.setup_scene()

    def setup_scene(self):
        self.scene.set_background(SCENE_BACKGROUND_COLOR)
        self.scene_widget.look_at(THIRD_PERSON_VIEW["center"], THIRD_PERSON_VIEW["eye"], THIRD_PERSON_VIEW["up"])


        self.scene_widget.enable_scene_caching(True)

    def setup_material(self):
        self.material = o3d.visualization.rendering.MaterialRecord()
        self.material.shader = MATERIAL_SHADER
        self.material.point_size = MATERIAL_POINT_SIZE

    def draw_scenes(self, points, ref_boxes, ref_labels, ref_scores):
        pts = o3d.geometry.PointCloud()
        pts.points = o3d.utility.Vector3dVector(points[:, :3])

        self.scene.clear_geometry()
        self.scene.add_geometry("points", pts, self.material)
        self.scene_widget.force_redraw()


class MediaControl:
    frame: gui.Vert
    progress_bar: gui.ProgressBar
    play_button: gui.Button

    def __init__(self):
        self.frame = gui.Horiz()
        self.play_button = gui.Button("Play/Pause")
        self.progress_bar = gui.ProgressBar()
        self.arrange_layout()

    def arrange_layout(self):
        self.frame.add_child(self.play_button)
        self.frame.add_child(self.progress_bar)
        self.frame.frame = gui.Rect(0, SCENE_HEIGHT, SCENE_WIDTH, WINDOW_HEIGHT-SCENE_HEIGHT)


class Settings:
    frame: gui.Vert

    def __init__(self):
        self.frame = gui.Vert()
        # TODO

    def arrange_layout(self):
        # TODO
        self.frame.frame = gui.Rect(SCENE_WIDTH, 0, WINDOW_WIDTH-SCENE_WIDTH, WINDOW_HEIGHT)


class Window(threading.Thread):
    window: gui.Window
    media: Media
    media_control: MediaControl
    settings: Settings
    has_initialized: bool
    running: bool

    def __init__(self):
        super().__init__()
        self.has_initialized = False

    def arrange_layout(self):
        self.window.add_child(self.media_control.frame)
        self.window.add_child(self.settings.frame)
        self.window.add_child(self.media.scene_widget)

    def run(self):
        self.running = True
        gui.Application.instance.initialize()
        self.window = gui.Application.instance.create_window(WINDOW_NAME, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.media = Media(self.window.renderer)
        self.media_control = MediaControl()
        self.settings = Settings()
        self.arrange_layout()
        self.has_initialized = True
        gui.Application.instance.run()
        self.running = False

    def draw_scenes(self, points, ref_boxes, ref_labels, ref_scores):#TODO: remove
        self.media.draw_scenes(points, ref_boxes, ref_labels, ref_scores)
