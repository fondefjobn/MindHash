import logging
import os
from typing import List, TypeVar, Dict

import numpy as np
import yaml
import tensorflow as tf
from easydict import EasyDict as edict
from ouster import client as cl
from yaml import SafeLoader
from waymo_open_dataset import dataset_pb2

from tools.structs.custom_structs import Ch, MatrixCloud

"""
@Module: Utilities
@Description: Provides general utility functions
@Authors: Radu Rebeja, Lubor Budaj
"""

# Global variables
def_numpy: str = '../resources/output/numpy'
def_json: str = '../resources/output/json'
def_pcap: str = '../resources/output/pcap_out'
_T = TypeVar("_T")
_K = TypeVar("_K")


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.CRITICAL)


def write(hm: Dict[_K, _T], k: _K, v: _T):
    """
    Write to dictionary
    Parameters
    ----------
    hm
    k
    v

    Returns
    -------

    """
    hm.update({k, v})


def edict_to_dict(edict_obj):
    dict_obj = {}

    for key, vals in edict_obj.items():
        if isinstance(vals, edict):
            dict_obj[key] = edict_to_dict(vals)
        else:
            dict_obj[key] = vals

    return dict_obj


def label_to_box(l, id):
    """
    Helper function for data extraction from tfrecord file
    @https://github.com/erksch/3D-object-tracking
    """
    return [
        l.box.center_x,
        l.box.center_y,
        l.box.center_z,
        l.box.width,
        l.box.length,
        l.box.height,
        l.box.heading,
        l.type,
        id,
    ]


def read_tfrecord(path):
    """
    Function for data extraction from tfrecord file
    The function is inspired by @https://github.com/erksch/3D-object-tracking
    path - path to tfrecord file
    output - list of frames. each frame is a list of boxes specified by [x,y,z,w,l,h,heading,label,id]
    """
    dataset = tf.data.TFRecordDataset([path])
    frames = []

    for data in dataset:
        frame = dataset_pb2.Frame()
        frame.ParseFromString(bytearray(data.numpy()))
        frames.append(frame)

    label_id_to_idx = {}
    output = []
    for i, frame in enumerate(frames):
        labels = frame.laser_labels

        labels = [label for label in labels if label.type != 3]

        for label in labels:
            if label.id not in label_id_to_idx:
                label_id_to_idx[label.id] = len(label_id_to_idx)

        detections = [label_to_box(label, label_id_to_idx[label.id]) for label in labels]
        output.append(detections)

    return output


class FileUtils:

    @staticmethod
    def load_file(path: str, ext: str, out=None):
        parserMap[ext](path, out)

    @staticmethod
    def __parse(src, dest: str):
        if src is not None:
            try:
                outputMap[dest]()
            except (OSError,):
                return None

    @staticmethod
    def safe_parsing(path: str, parse_f, out=None, *args, **kwargs):
        """
        Function executing any parsing method to load files
        If `out` is specified, execute specific output function
        otherwise returns the parsed values
        Parameters
        ----------
        path
        parse_f
        out
        args
        kwargs
        """
        try:
            with open(path) as f:
                if out is not None:
                    return FileUtils.__parse(parse_f(f, *args, **kwargs), out)
                else:
                    return parse_f(f, *args, **kwargs)
        except (OSError, yaml.YAMLError):
            logging.critical(msg='Error loading file')
            return None

    @staticmethod
    def parse_yaml(path: str, out=None):
        return FileUtils.safe_parsing(path, yaml.load, out=out, Loader=SafeLoader)

    class Output:
        """Convert objects and save in specified file format"""

        @staticmethod
        def to_numpy_bulk(frame_ls: List[np.ndarray], path: str, names: List[str] = None):
            FileUtils.Dir.mkdir_here(path)
            if not names:
                for ix, o in enumerate(frame_ls):
                    np.save(os.path.join(path, str(ix)), o)
            else:
                for ix, o in enumerate(frame_ls):
                    o.tofile(os.path.join(path, names[ix]))

        @staticmethod
        def to_numpy(frame: np.ndarray, path: str, name: str):

            np.save(os.path.join(path, name), frame)

        @staticmethod
        def to_json():
            pass

    class Dir:

        @staticmethod
        def mkdir_here(*path: str, sep='/'):
            """
            creates a directory
            """
            current_directory = os.getcwd()
            final_directory = os.path.join(current_directory, sep.join(path))
            if not os.path.exists(final_directory):
                os.makedirs(final_directory)


class Cloud3dUtils:

    @staticmethod
    def to_pcdet(matrix_cloud: MatrixCloud):
        # only store return signal intensity
        # field_vals = matrix_cloud.channels[Ch.SIGNAL]
        # field_vals = ArrayUtils.norm_zero_one(field_vals)
        # get all data as one H x W x n (inputs) int64 array
        x = matrix_cloud.clouds[Ch.XYZ][0]
        y = matrix_cloud.clouds[Ch.XYZ][1]
        z = matrix_cloud.clouds[Ch.XYZ][2]
        frame = np.column_stack((x, y, z, np.zeros(x.shape[0], dtype=float)))
        return frame


class ArrayUtils:

    @staticmethod
    def norm_zero_one(data: np.ndarray):
        """Normalize array values to [0,1]"""
        return (data - np.min(data)) / (np.max(data) - np.min(data))

    @staticmethod
    def np_dict_to_list(data: dict):
        """
        Convert dict of numpy arrays to dict of primitive lists
        with dictionary comprehension
        ----------
        data

        Returns
        -------

        """
        return {key: arr.tolist() for (key, arr) in data.items()}


parserMap = {
    'yaml': FileUtils.parse_yaml,
    'csv': None,
    'las': None,
    'json': None,
}

outputMap = {
    'npy': FileUtils.Output.to_numpy_bulk,
    'json': FileUtils.Output.to_json
}
