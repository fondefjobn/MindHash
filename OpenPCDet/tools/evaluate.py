import argparse
import json
import sys
from pathlib import Path
from threading import Event
from time import sleep

import numpy as np
import open3d
import torch
from open3d.cpu.pybind.visualization import Visualizer

from OpenPCDet.tools.visual_utils.open3d_vis_utils import draw_box
from OpenPCDet.pcdet.config import cfg, cfg_from_yaml_file
from pcdet.datasets import DatasetTemplate
from pcdet.models import build_network, load_data_to_gpu
from pcdet.utils import common_utils
from tools.pipes.p_template import State, RoutineSet
from tools.structs.custom_structs import PopList

OPEN3D_FLAG = True
base_path = Path(__file__).parent
file_path = "../OpenPCDet/tools/"
ds_cfgs = {
    'PVRCNN': "cfgs/kitti_models/pv_rcnn.yaml"
}


class Routines(RoutineSet):
    def_npy = 'MindHash/OpenPCDet/tools/format.npy'

    def id(self):
        return 'EVAL_BUNDLE'

    def Evaluate(self, state: State, *args):
        npy_ls = args[1]
        x = 0
        logger = common_utils.create_logger()
        config = str((base_path / ds_cfgs[state.args.ml]).resolve())
        config = cfg_from_yaml_file(config, cfg, rel_path=file_path)
        dyn_dataset = DemoDataset(config.DATA_CONFIG, class_names=config.CLASS_NAMES, training=False,
                                  root_path=(base_path / self.def_npy).resolve(), logger=logger,
                                  frames=args[0])
        model = build_net(state.args.mlpath, dyn_dataset,
                          logger, config=config)
        with torch.no_grad():
            x = 0
            while not (args[0].full() and x > len(args[0])):#Merge this
                data_dict = dyn_dataset[x]
                logger.info(f'Processed frame index: \t{x + 1}')
                data_dict = dyn_dataset.collate_batch([data_dict])

                load_data_to_gpu(data_dict)
                pred_dicts, _ = model.forward(data_dict)
                out = {
                    'ref_boxes': pred_dicts[0]['pred_boxes'].cpu().tolist(),
                    'ref_scores': pred_dicts[0]['pred_scores'].cpu().tolist(),
                    'ref_labels': pred_dicts[0]['pred_labels'].cpu().tolist()
                }
                o = {"points": args[0][x], "predictions": out}
                npy_ls.add(o)
                x += 1
        if any("predictions" in o for o in state.args.export):  # } move this to export local
            with open('../resources/output/json/out.json', 'w+') as f:
                json.dump(npy_ls, f)


class DemoDataset(DatasetTemplate):
    def __init__(self, dataset_cfg, class_names, training=True, root_path=None, logger=None, ext='.npy', frames=None):
        """
        Args:
            root_path:
            dataset_cfg:
            class_names:
            training:
            logger:
        """
        super().__init__(
            dataset_cfg=dataset_cfg, class_names=class_names, training=training, root_path=root_path, logger=logger
        )
        self.frames: PopList = frames
        self.event = Event()
        self.ext = ext

    def __len__(self):
        return len(self.sample_file_list)

    def __getitem__(self, index):
        if self.ext == '.bin':
            points = np.fromfile(self.sample_file_list[index], dtype=np.float32).reshape(-1, 4)
        elif self.ext == '.npy':
            points = self.frames.get(index, self.event)
        else:
            raise NotImplementedError
        input_dict = {
            'points': points,
            'frame_id': index,
        }
        data_dict = self.prepare_data(data_dict=input_dict)
        return data_dict


def parse_config():
    parser = argparse.ArgumentParser(description='arg parser')
    parser.add_argument('--cfg_file', type=str, default='cfgs/kitti_models/second.yaml',
                        help='specify the config for demo')
    parser.add_argument('--data_path', type=str, default='demo_data',
                        help='specify the point cloud data file or directory')
    parser.add_argument('--ckpt', type=str, default=None, help='specify the pretrained model')
    parser.add_argument('--ext', type=str, default='.bin', help='specify the extension of your point cloud data file')

    args = parser.parse_args()

    cfg_from_yaml_file(args.cfg_file, cfg, None)

    return args, cfg


def draw_scenes(vis: Visualizer, pts, points, gt_boxes=None, ref_boxes=None, ref_labels=None, ref_scores=None,
                point_colors=None,
                draw_origin=True):
    if isinstance(points, torch.Tensor):
        points = points.cpu().numpy()
    if isinstance(gt_boxes, torch.Tensor):
        gt_boxes = gt_boxes.cpu().numpy()
    if isinstance(ref_boxes, torch.Tensor):
        ref_boxes = ref_boxes.cpu().numpy()

    vis.clear_geometries()

    pts.points = open3d.utility.Vector3dVector(points[:, :3])

    vis.add_geometry(pts)
    if point_colors is None:
        pts.colors = open3d.utility.Vector3dVector(np.ones((points.shape[0], 3)))
    else:
        pts.colors = open3d.utility.Vector3dVector(point_colors)

    if gt_boxes is not None:
        vis = draw_box(vis, gt_boxes, (0, 0, 1))

    if ref_boxes is not None:
        vis = draw_box(vis, ref_boxes, (0, 1, 0), ref_labels, ref_scores)

    vis.update_geometry(pts)
    vis.poll_events()
    vis.update_renderer()


def build_net(ckpt, init_dataset, logger, config=cfg):
    model = build_network(model_cfg=config.MODEL, num_class=len(config.CLASS_NAMES), dataset=init_dataset)
    model.load_params_from_file(filename=ckpt, logger=logger, to_cpu=True)
    model.cuda()
    model.eval()
    return model


obj_labels = {
    1: 'Car',
    2: 'Pedestrian',
    3: 'Cyclist'
}


def evaluate(model, dataset, logger):
    for idx, data_dict in enumerate(dataset):
        logger.info(f'Visualized sample index: \t{idx + 1}')
        data_dict = dataset.collate_batch([data_dict])
        load_data_to_gpu(data_dict)
        pred_dicts, _ = model.forward(data_dict)
        out = {
            'ref_boxes': pred_dicts[0]['pred_boxes'].cpu().tolist(),
            'ref_scores': pred_dicts[0]['pred_scores'].cpu().tolist(),
            'ref_labels': [obj_labels[x] for x in pred_dicts[0]['pred_labels'].cpu().tolist()]
        }
        logger.info('Processing done.')
        return out


def main():
    args, cfg = parse_config()
    logger = common_utils.create_logger()
    demo_dataset = DemoDataset(
        dataset_cfg=cfg.DATA_CONFIG, class_names=cfg.CLASS_NAMES, training=False,
        root_path=Path(args.data_path), ext=args.ext, logger=logger
    )
    logger.info(f'Total number of samples: \t{len(demo_dataset)}')

    model = build_network(model_cfg=cfg.MODEL, num_class=len(cfg.CLASS_NAMES), dataset=demo_dataset)
    model.load_params_from_file(filename=args.ckpt, logger=logger, to_cpu=True)
    model.cuda()
    model.eval()
    vis = Visualizer()
    vis.create_window()
    vis.get_render_option().point_size = 1.0
    vis.get_render_option().background_color = np.zeros(3)
    pts = open3d.geometry.PointCloud()
    with torch.no_grad():
        for idx, data_dict in enumerate(demo_dataset):
            logger.info(f'Visualized sample index: \t{idx + 1}')
            data_dict = demo_dataset.collate_batch([data_dict])
            load_data_to_gpu(data_dict)
            pred_dicts, _ = model.forward(data_dict)
            #with open('../../resources/output/json/out.json', 'w') as f:
             #   o = {
              #      'ref_boxes': pred_dicts[0]['pred_boxes'].cpu().tolist(),
             #       'ref_scores': pred_dicts[0]['pred_scores'].cpu().tolist(),
             #       'ref_labels': pred_dicts[0]['pred_labels'].cpu().tolist()
             #   }
             #   json.dump(o, f)
            draw_scenes(vis, pts, points=data_dict['points'][:, 1:], ref_boxes=pred_dicts[0]['pred_boxes'],
                        ref_scores=pred_dicts[0]['pred_scores'],
                        ref_labels=pred_dicts[0]['pred_labels'])
            sleep(0.01)
    logger.info('Demo done.')


if __name__ == '__main__':
    main()

#
# V.draw_scenes(
#                points=data_dict['points'][:, 1:], ref_boxes=pred_dicts[0]['pred_boxes'],
#                ref_scores=pred_dicts[0]['pred_scores'], ref_labels=pred_dicts[0]['pred_labels']
#            )
