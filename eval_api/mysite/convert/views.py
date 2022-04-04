import glob
from pathlib import Path

import numpy as np
import torch
from django.http import HttpResponse

from django.shortcuts import render

from OpenPCDet.pcdet.config import cfg, cfg_from_yaml_file
from pcdet.datasets import DatasetTemplate
from pcdet.utils import common_utils

from OpenPCDet.tools.evaluate import build_net, EvalDataset, evaluate
from utilities.mh_parser import SAParser
from .forms import sendableFile
import numpy
from eval_api.mysite.manage import cfg_file, relative_path

ckpt = relative_path + 'pv_rcnn.pth'
data = relative_path + 'format.npy'
ext = '.npy'
logger = common_utils.create_logger()
config = cfg_from_yaml_file(cfg_file, cfg, rel_path=relative_path)
demo_dataset = EvalDataset(
    dataset_cfg=config.DATA_CONFIG, class_names=config.CLASS_NAMES, training=False,
    root_path=Path(data), ext=ext, logger=logger
)
model = build_net(ckpt, demo_dataset, logger, config=config)


class RequestDset(DatasetTemplate):
    def __init__(self, dataset_cfg, class_names, training=True, root_path=None, logger=None, ext='.bin', array=None):
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
        self.root_path = root_path
        self.ext = ext
        data_file_list = glob.glob(str(root_path / f'*{self.ext}')) if self.root_path.is_dir() else [self.root_path]
        self.sample_file_list = data_file_list
        self.input = array

    def __len__(self):
        return 1

    def __getitem__(self, index):
        if self.ext == '.bin':
            points = np.fromfile(self.sample_file_list[index], dtype=np.float32).reshape(-1, 4)
        elif self.ext == '.npy':
            points = self.input
        else:
            raise NotImplementedError
        input_dict = {
            'points': points,
            'frame_id': index,
        }
        data_dict = self.prepare_data(data_dict=input_dict)
        return data_dict


def to_dataset(points) -> DatasetTemplate:
    return RequestDset(dataset_cfg=config.DATA_CONFIG, class_names=config.CLASS_NAMES, training=False,
                       root_path=Path(data), ext=ext, logger=logger, array=points)


def convert(request):
    if request.method == "GET":
        form = sendableFile()
        return render(request, "convert.html", {"form": form})

    elif request.method == "POST":
        form = sendableFile(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data["file"]
            scene = numpy.load(file)
            ds = to_dataset(scene)
            with torch.no_grad():
                out = SAParser(evaluate(model, ds, logger)).to_json()

            return HttpResponse(out)

        return HttpResponse("failed")
