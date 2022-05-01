from pathlib import Path
from threading import Event
from typing import List, Tuple

import torch
from pcdet.datasets import DatasetTemplate
from pcdet.models import build_network, load_data_to_gpu
from pcdet.utils import common_utils

from OpenPCDet.pcdet.config import cfg, cfg_from_yaml_file
from tools.pipes import RNode
from tools.structs.custom_structs import PopList

"""
@Module: OpenPCDet Evaluate 
@Description: 
@Author: pcdet
@ModifiedBy: Radu Rebeja
"""

# Global variables
OPEN3D_FLAG = True
base_path = Path(__file__).parent
file_path = "../OpenPCDet/tools/"
ds_cfgs = {
    'PVRCNN': "cfgs/kitti_models/pv_rcnn.yaml",
    'POINTRCNN': "cfgs/kitti_models/pointrcnn.yaml",
    'POINTPILLAR': "cfgs/kitti_models/pointpillar_pyramid_aug.yaml",
    'PARTA2': "cfgs/kitti_models/PartA2_free.yaml",
    'PP_NU': "cfgs/nuscenes_models/cbgs_voxel0075_res3d_centerpoint.yaml"
    # PP_NU requires different shape [x,y,z,intensity,timestamp/0]

}

labels = {
    1: 'Car',
    2: 'Pedestrian',
    3: 'Cyclist'
}


class EvalDataset(DatasetTemplate):
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
        points = self.frames.get(index, self.event)
        input_dict = {
            'points': points,
            'frame_id': index,
        }
        data_dict = self.prepare_data(data_dict=input_dict)
        return data_dict


class Routines(RNode):
    """
    3D-Detector routine
    """
    @classmethod
    def script(cls, parser) -> bool:
        return False

    def_npy = 'MindHash/OpenPCDet/tools/format.npy'

    def __init__(self, state):
        super().__init__(state)

    @RNode.assist
    def run(self, _input: List[PopList], output: PopList, **kwargs):
        state = self.state
        state['labels'] = labels
        logger = common_utils.create_logger()
        config = str((base_path / ds_cfgs[state.args.ml]).resolve())
        config = cfg_from_yaml_file(config, cfg, rel_path=file_path)
        dyn_dataset = EvalDataset(config.DATA_CONFIG, class_names=config.CLASS_NAMES, training=False,
                                  root_path=(base_path / self.def_npy).resolve(), logger=logger,
                                  frames=_input[0])
        model = build_net(state.args.mlpath, dyn_dataset,
                          logger, config=config)
        with torch.no_grad():
            x = 0
            while not _input[0].full(x):
                data_dict = dyn_dataset[x]
                logger.info(f'Processed frame index: \t{x + 1}')
                data_dict = dyn_dataset.collate_batch([data_dict])
                load_data_to_gpu(data_dict)
                pred_dicts, _ = model.forward(data_dict)
                out = {
                    'ref_boxes': pred_dicts[0]['pred_boxes'].cpu().numpy(),
                    'ref_scores': pred_dicts[0]['pred_scores'].cpu().numpy(),
                    'ref_labels': pred_dicts[0]['pred_labels'].cpu().numpy()
                }
                output.append(out)
                x += 1

    def dependencies(self):
        from streamprocessor.stream_process import Routines as processor
        return [processor]


def build_net(ckpt, init_dataset, logger, config=cfg):
    model = build_network(model_cfg=config.MODEL, num_class=len(config.CLASS_NAMES), dataset=init_dataset)
    model.load_params_from_file(filename=ckpt, logger=logger, to_cpu=True)
    model.cuda()
    model.eval()
    return model


def main():
    pass


if __name__ == '__main__':
    main()
