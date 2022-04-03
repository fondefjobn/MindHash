from threading import Event

import numpy as np
import open3d
import torch
from open3d.visualization import Visualizer as Viz

from tools.pipes import RoutineSet
from tools.structs import PopList
from OpenPCDet.tools.visual_utils.open3d_vis_utils import draw_box


class Routines(RoutineSet):

    def id(self):
        return 'VIZ_BUNDLE'

    def Visualization(self, state, *args):
        in_ls: PopList = args[0]
        vis = Viz()
        vis.create_window()
        vis.get_render_option().point_size = 1.0
        vis.get_render_option().background_color = np.zeros(3)
        pts = open3d.geometry.PointCloud()
        x = 0
        e = Event()
        while not in_ls.full(x):
            frame = in_ls.get(x, e)
            data_dict = frame["points"]
            pred_dicts = frame["predictions"]

            draw_scenes(vis, pts, points=data_dict['points'][:, 1:], ref_boxes=pred_dicts['pred_boxes'],
                        ref_scores=pred_dicts['pred_scores'],
                        ref_labels=pred_dicts['pred_labels'])
            x += 1


def draw_scenes(vis: Viz, pts, points, gt_boxes=None, ref_boxes=None, ref_labels=None, ref_scores=None,
                point_colors=None,
                draw_origin=True):
    # removed from tensor to cpu

    vis.clear_geometries()



    vis.add_geometry(pts)
    if point_colors is None:
        pts.colors = open3d.utility.Vector3dVector(np.ones((points.shape[0], 3)))
    else:
        pts.colors = open3d.utility.Vector3dVector(point_colors)

    if gt_boxes is not None:
        vis = draw_box(vis, gt_boxes, (0, 0, 1))

    if ref_boxes is not None:
        vis = draw_box(vis, ref_boxes, (0, 1, 0), ref_labels, ref_scores)

    pts.points = open3d.utility.Vector3dVector(points[:, :3])

    vis.update_geometry(pts)
    vis.poll_events()
    vis.update_renderer()


class Visualizer:

    def __init__(self):
        pass
