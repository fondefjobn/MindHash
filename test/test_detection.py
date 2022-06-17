import argparse
import unittest
from cmath import inf
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, List, Any

import torch
from easydict import EasyDict
from numpy import shape
from pcdet.config import cfg
from pcdet.models import load_data_to_gpu

from OpenPCDet.pcdet.config import cfg_from_yaml_file
from OpenPCDet.tools.detection import Routines as R_Eval, EvalDataset, build_net, ds_cfgs
from sensor.sensor_controller import Routines as Input
from streamprocessor.stream_process import Routines as R_Prc
from tools.pipeline import Pipeline, State
from tools.pipeline import RNode
from tools.pipeline.routines import RoutineSet
from tools.structs import PopList

file_path = "../OpenPCDet/tools/" + ds_cfgs["PVRCNN++"]
base_path = Path(__file__).parent
OUTPUT_IOBOX: str = "outputIOBOX"
OUTPUT_MLSTDN: str = "outputMLSTDN"
OUTPUT_MLCLASSES: str = "outputCLASSES"
CKPT_PATH: str = "resources/trained_models/pvrcnn++_epoch_82.pth"


@dataclass(frozen=True)
class Args:
    """
    Dummy namespace dataclass
    """
    host = None
    PCAP = None
    META = None
    port = None
    n = 200
    sensor = "ouster"
    mlpath: str = "resources/trained_models/pvrcnn++_epoch_82.pth"
    ml: str.upper = "PVRCNN++"
    input = "resources/pcap/OS1-128_Rev-05_Urban-Drive.pcap"
    meta = "resources/pcap/OS1-128_Rev-05_Urban-Drive.json"
    live: bool = False
    th: float = 0.7


@dataclass(frozen=True)
class TestStreetAnalytics(RoutineSet):
    def activationList(self, a: argparse.Namespace) -> List[Tuple[object, RNode]]:
        return [(True, Input),
                (True, R_Prc),
                (True, TestDetector),
                ]

    def __all__(self) -> set:
        return {Input, R_Prc, TestDetector}


class TestDetector(RNode):
    """
    3D-Detector routine
    """
    ix: int = 0

    def get_index(self) -> int:
        return self.ix

    model_config: EasyDict = None

    def_npy = 'MindHash/OpenPCDet/tools/format.npy'

    def __init__(self, state):
        super().__init__(state)
        self.logger = self.state.logger
        config = base_path / file_path
        self.model_config = cfg_from_yaml_file(config, cfg, rel_path="OpenPCDet/tools/")
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
        Custom run method for testing
        """

        logger = self.logger
        config = self.model_config
        dyn_dataset = EvalDataset(config.DATA_CONFIG, class_names=config.CLASS_NAMES, training=False,
                                  root_path=None, logger=logger,
                                  frames=_input[0])
        model = build_net(self.state.args.mlpath, dyn_dataset,
                          logger, config=config)
        class_set: set = set()

        with torch.no_grad():
            while not _input[0].full(self.ix):
                data_dict = dyn_dataset[self.ix]
                logger.info(f'Processed frame index: \t{self.ix + 1}')
                data_dict = dyn_dataset.collate_batch([data_dict])
                load_data_to_gpu(data_dict)  # inspect this step
                pred_dicts, _ = model.forward(data_dict)
                out = {
                    'ref_boxes': pred_dicts[0]['pred_boxes'].cpu().numpy(),
                    'ref_scores': pred_dicts[0]['pred_scores'].cpu().numpy(),
                    'ref_labels': pred_dicts[0]['pred_labels'].cpu().numpy()
                }
                if len(out['ref_boxes']) > 0:
                    self.state[OUTPUT_IOBOX] = out['ref_boxes'][0]
                    self.state[OUTPUT_MLSTDN] = out['ref_boxes']
                    class_set.update([_ for _ in list(out['ref_labels'])])
                    self.state[OUTPUT_MLCLASSES] = len(class_set)
                    if len(class_set) == 3:
                        self.ix = inf
                        break
                self.ix += 1

    def dependencies(self):
        from streamprocessor.stream_process import Routines as processor
        return [processor]


def init_pipeline() -> (Pipeline, State):
    parser = argparse.ArgumentParser(description='StreetAnalytics Project CLI')
    pd = Pipeline(testing=True)
    state = State(parser=parser)
    state.args = Args()
    state = pd.build_pipeline(state=state, rs=TestStreetAnalytics())
    return pd, state


class DetectionTests(unittest.TestCase):
    CLASSES: int = 3

    def test_IOBOX(self):
        pd, state = init_pipeline()
        pd.execute_pipeline()
        self.assertTupleEqual(shape(state[OUTPUT_IOBOX]), (7,))

    def test_MLSTDNSEG(self):
        pd, state = init_pipeline()
        pd.execute_pipeline()
        self.assertTrue(shape(state[OUTPUT_MLSTDN])[0] > self.CLASSES)

    def test_MLCLASS(self):
        pd, state = init_pipeline()
        pd.execute_pipeline()
        self.assertEqual(state.state[OUTPUT_MLCLASSES], self.CLASSES)


if __name__ == '__main__':
    unittest.main()
