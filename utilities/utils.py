import logging
import os
import traceback
from typing import List, TypeVar, Dict

import numpy as np
import yaml
from easydict import EasyDict as edict
from numba import jit
from numpy import ndarray
from ouster import client as cl
from yaml import SafeLoader

from tools.structs.custom_structs import Ch, MatrixCloud
"""
@Module: Utilities
@Description: Provides general utility functions
@Author: Radu Rebeja
"""

# Global variables
def_numpy: str = '../resources/output/numpy'
def_json: str = '../resources/output/json'
def_pcap: str = '../resources/output/pcap_out'
_T = TypeVar("_T")
_K = TypeVar("_K")

"""

if classes become bloated we split per module
"""

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
            traceback.print_exc()
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
        x = matrix_cloud.X
        y = matrix_cloud.Y
        z = matrix_cloud.Z
        sig = ArrayUtils.norm_zero_one(matrix_cloud.channels[Ch.SIGNAL])
        elon = np.zeros(x.shape[0], dtype=float)
        sectors = np.array_split(np.column_stack((x, y, z, sig.flatten(), elon)), indices_or_sections=4, axis=0)
        sectors = np.concatenate((sectors[1], sectors[2]))
        return sectors

class ArrayUtils:

    @staticmethod
    def norm_zero_one(data: np.ndarray) -> ndarray:
        """Normalize array values to [0,1]"""
        return (data - np.min(data))/np.ptp(data)

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
