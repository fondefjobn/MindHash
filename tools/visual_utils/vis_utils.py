import open3d
import matplotlib
import numpy as np

"""
@Module:VisUtils
@Description: Open3d visualization tool box largely based on OpenPCDet/tools/visual_utils/open3d_vis_utils,
but with added support for moving pointclouds.
@Author: Jihan Yang
@ModifiedBy: Bob van der Vuurst
"""

box_colormap = [
    [1, 1, 1],
    [0, 1, 0],
    [0, 1, 1],
    [1, 1, 0],
]

CONFIG = "../tools/visual_utils/camera_cfg.json"


class VisUtils:
    vis: open3d.visualization.Visualizer
    camera: open3d.camera

    def __init__(self):
        self.vis = open3d.visualization.Visualizer()
        self.vis.create_window()
        self.vis.get_render_option().point_size = 1.0
        self.vis.get_render_option().background_color = np.zeros(3)
        self.get_camera_cfg()

    def get_camera_cfg(self):
        self.camera = open3d.io.read_pinhole_camera_parameters(CONFIG)

    def get_coor_colors(self, obj_labels):
        """
        Args:
            obj_labels: 1 is ground, labels > 1 indicates different instance cluster
        Returns:
            rgb: [N, 3]. color for each point.
        """
        colors = matplotlib.colors.XKCD_COLORS.values()
        max_color_num = obj_labels.max()

        color_list = list(colors)[:max_color_num + 1]
        colors_rgba = [matplotlib.colors.to_rgba_array(color) for color in color_list]
        label_rgba = np.array(colors_rgba)[obj_labels]
        label_rgba = label_rgba.squeeze()[:, :3]

        return label_rgba

    def reset_view(self):
        view_control = self.vis.get_view_control()
        view_control.convert_from_pinhole_camera_parameters(self.camera)

    def draw_scenes(self, points, gt_boxes=None, ref_boxes=None, ref_labels=None, ref_scores=None, point_colors=None):
        vis = self.vis
        vis.clear_geometries()

        pts = open3d.geometry.PointCloud()
        pts.points = open3d.utility.Vector3dVector(points[:, :3])
        vis.add_geometry(pts)

        if point_colors is None:
            pts.colors = open3d.utility.Vector3dVector(np.ones((points.shape[0], 3)))
        else:
            pts.colors = open3d.utility.Vector3dVector(point_colors)

        if gt_boxes is not None:
            self.draw_box(gt_boxes, (0, 0, 1))

        if ref_boxes is not None:
            self.draw_box(ref_boxes, (0, 1, 0), ref_labels, ref_scores)

        self.reset_view()
        vis.poll_events()
        vis.update_renderer()

    def translate_boxes_to_open3d_instance(self, gt_boxes):
        """
                 4-------- 6
               /|         /|
              5 -------- 3 .
              | |        | |
              . 7 -------- 1
              |/         |/
              2 -------- 0
        """
        center = gt_boxes[0:3]
        lwh = gt_boxes[3:6]
        axis_angles = np.array([0, 0, gt_boxes[6] + 1e-10])
        rot = open3d.geometry.get_rotation_matrix_from_axis_angle(axis_angles)
        box3d = open3d.geometry.OrientedBoundingBox(center, rot, lwh)

        line_set = open3d.geometry.LineSet.create_from_oriented_bounding_box(box3d)

        # import ipdb; ipdb.set_trace(context=20)
        lines = np.asarray(line_set.lines)
        lines = np.concatenate([lines, np.array([[1, 4], [7, 6]])], axis=0)

        line_set.lines = open3d.utility.Vector2iVector(lines)

        return line_set, box3d

    def draw_box(self, gt_boxes, color=(0, 1, 0), ref_labels=None, score=None):
        for i in range(gt_boxes.shape[0]):
            line_set, box3d = self.translate_boxes_to_open3d_instance(gt_boxes[i])
            if ref_labels is None:
                line_set.paint_uniform_color(color)
            else:
                line_set.paint_uniform_color(box_colormap[ref_labels[i]])

            self.vis.add_geometry(line_set)