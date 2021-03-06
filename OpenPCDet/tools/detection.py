from pathlib import Path
from threading import Event
from typing import List, Tuple

import torch
from easydict import EasyDict
from pcdet.datasets import DatasetTemplate
from pcdet.models import build_network, load_data_to_gpu
from pcdet.utils import common_utils

from OpenPCDet.pcdet.config import cfg, cfg_from_yaml_file
from tools.pipeline import RNode, State
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
    """
    Dataset configs
    """
    'PVRCNN': "cfgs/kitti_models/pv_rcnn.yaml",
    "PVRCNN++": "cfgs/waymo_models/pv_rcnn_plusplus.yaml",
    'POINTRCNN': "cfgs/kitti_models/pointrcnn.yaml",
    'POINTPILLAR': "cfgs/kitti_models/pointpillar_pyramid_aug.yaml",
    'POINTPILLAR++': "cfgs/waymo_models/pointpillar_1x.yaml",
    'PARTA2': "cfgs/kitti_models/PartA2_free.yaml",
    'PP_NU': "cfgs/nuscenes_models/cbgs_voxel0075_res3d_centerpoint.yaml"
    # PP_NU requires different shape [x,y,z,intensity,timestamp/0]
}

CLS_LABELS = {
    1: 'Car',
    2: 'Pedestrian',
    3: 'Cyclist'
}


class EvalDataset(DatasetTemplate):
    def __init__(self, dataset_cfg, class_names, training=True, root_path=None, logger=None, ext='.npy', frames=None):
        """
        Parameters
        ----------
        dataset_cfg : EasyDict
        class_names : dict
        training : bool
        root_path :
        logger : logging.Logger
        ext : str
        frames : input list
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
        points = self.frames.qy(index, self.event)
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
    ix: int = 0

    def get_index(self) -> int:
        return self.ix

    model_config: EasyDict = None

    @classmethod
    def script(cls, parser) -> bool:
        parser.add_argument('--eval',
                            help='Evaluate input with a ML Model', action="store_true")
        parser.add_argument('--ml', type=str.upper, default='PVRCNN', choices=['PVRCNN', 'PVRCNN++', 'POINTRCNN',
                                                                               'POINTPILLAR', 'POINTPILLAR++',
                                                                               'PARTA2', 'PP_NU'],
                            help='Model name')
        parser.add_argument('--mlpath', type=str, default=None, help='Model path from content root')
        parser.add_argument('--th', type=float, default=0.3, help='Detections score threshold ')
        return True

    def_npy = 'MindHash/OpenPCDet/tools/format.npy'

    def __init__(self, state):
        super().__init__(state)
        self.logger = self.state.logger
        config = str((base_path / ds_cfgs[state.args.ml]).resolve())
        self.model_config = cfg_from_yaml_file(config, cfg, rel_path=file_path)
        self.custom_config(state)

    def custom_config(self, state: State):
        """
        User-defined detection configuration parameters
        Parameters
        ----------
        state : State

        Returns
        -------

        """
        args = state.args
        config = self.model_config
        config.MODEL.POST_PROCESSING.SCORE_THRESH = args.th if args.th < 1 else 0.3

    @RNode.assist
    def run(self, _input: List[PopList], output: PopList, **kwargs):
        """
        Create dataset class
        Build network using the provided configuration
        Every frame is loaded to gpu and evaluated
        Output is provided as a tensor that should be loaded back to cpu
        & converted to numpy array
        Parameters
        ----------
        _input : input lists
        output : output list
        kwargs : optional kwargs ({})

        Returns
        -------

        """
        state = self.state
        logger = self.logger
        config = self.model_config
        dyn_dataset = EvalDataset(config.DATA_CONFIG, class_names=config.CLASS_NAMES, training=False,
                                  root_path=None, logger=logger,
                                  frames=_input[0])
        model = build_net(state.args.mlpath, dyn_dataset,
                          logger, config=config)
        with torch.no_grad():
            while not _input[0].full(self.ix):
                data_dict = dyn_dataset[self.ix]
                logger.info(f'Processed frame index: \t{self.ix + 1}')
                data_dict = dyn_dataset.collate_batch([data_dict])
                load_data_to_gpu(data_dict)  # inspect this step
                pred_dicts, _ = model.forward(data_dict)
                out = {
                    'ref_boxes': pred_dicts[0]['pred_boxes'].cpu().numpy(),  # inspect time
                    'ref_scores': pred_dicts[0]['pred_scores'].cpu().numpy(),
                    'ref_labels': pred_dicts[0]['pred_labels'].cpu().numpy()
                }
                output.append(out)
                self.ix += 1

    def dependencies(self):
        from streamprocessor.stream_process import Routines as processor
        return [processor]


def build_net(ckpt: str, init_dataset: DatasetTemplate, logger, config=cfg):
    """
    Builds network using PCDet framework methods using the torch library
    Parameters
    ----------
    ckpt : checkpoint .PTH file
    init_dataset : dataset class
    logger :
    config : EasyDict

    Returns
    -------

    """
    model = build_network(model_cfg=config.MODEL, num_class=len(config.CLASS_NAMES), dataset=init_dataset)
    model.load_params_from_file(filename=ckpt, logger=logger, to_cpu=True)
    model.cuda()
    model.eval()
    return model


def main():
    pass


if __name__ == '__main__':
    main()
