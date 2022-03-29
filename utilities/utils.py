import logging
import os
from threading import Event
from typing import List, TypeVar, Dict
from easydict import EasyDict as edict
import numpy as np
import yaml
from ouster import client, pcap
from ouster import client as cl
from yaml import SafeLoader

from tools.pipes import RoutineSet, State
from utilities.custom_structs import PopList

def_numpy: str = '../resources/output/numpy'
def_json: str = '../resources/output/json'
def_pcap: str = '../resources/output/pcap_out'
_T = TypeVar("_T")
_K = TypeVar("_K")

"""
Utilities Module
if classes become bloated we split per module
"""
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.CRITICAL)


class Routines(RoutineSet):

    def id(self):
        return 'UTILS_BUNDLE'

    def UserInput(self, state: State, *args):
        """
        Routine: User Input File process

        Produces: UserInput
        Consumes: User provided input
        Requires: Pcap path
        Parameters
        ----------
        state
        args (input_list, output_list)

        Returns
        -------

        """
        with open(state.args.meta, 'r') as f:
            out_ls: PopList = args[1]
            getattr(IO, state.args.sensor)(state, f, out_ls)
            out_ls.set_full()
        Routines.logging.info(msg='UserInput reading: done')

    def ExportLocal(self, state: State, *args):
        """
         Routine: Export conversion results

         Produces: None

         Consumes: PcapList

         Requires: None
         """
        Routines.logging.info(msg='Export:STARTED')
        x = 0
        e = Event()
        in_ls = args[0]
        FileUtils.Dir.mkdir_here(def_numpy)
        while x < len(in_ls) or not in_ls.full():
            out = in_ls.get(x, e)
            FileUtils.Output.to_numpy(out, def_numpy, str(x))
            x += 1
        Routines.logging.info(msg='Export: done')


class Ch:
    RANGE = 'RANGE'
    NEAR_IR = 'NEAR_IR'
    REFLECTIVITY = 'REFLECTIVITY'
    SIGNAL = 'SIGNAL'
    XYZ = 'XYZ'
    channel_arr = [RANGE, SIGNAL, NEAR_IR, REFLECTIVITY]  # exact order of fields


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


class MatrixCloud:
    def __init__(self):
        self.timestamps = None
        self.clouds = {'xyz': None}
        self.channels = {}


class Cloud3dUtils:

    @staticmethod
    def get_matrix_cloud(xyzlut: cl.XYZLut, scan, channel_arr: List[str]) -> MatrixCloud:
        """"Create separate XYZ point-clouds for separate channels.
            Reading from cloud is done through dict destructuring.
            For keys use the client.ChanFields RANGE | SIGNAL | NEAR_IR | REFLECTIVITY"""
        matrix_cloud = MatrixCloud()
        field_names = channel_arr

        # use integer mm to avoid loss of precision casting timestamps
        xyz = (xyzlut(scan.field(cl.ChanField.RANGE))).astype(float)

        for ix, ch in enumerate(scan.fields):
            f = scan.field(ch)
            matrix_cloud.channels[field_names[ix]] = f
        x, y, z = [c.flatten() for c in np.dsplit(xyz, 3)]
        matrix_cloud.clouds[Ch.XYZ] = [x, y, z]
        return matrix_cloud

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
        # frame = client.destagger(metadata, frame)  # verify de-stagger
        # frame.reshape(-1, frame.shape[2])  # verify change
        # print(frame.shape)
        return frame


class ArrayUtils:

    @staticmethod
    def norm_zero_one(data: np.ndarray):
        """Normalize array values to [0,1]"""
        return (data - np.min(data)) / (np.max(data) - np.min(data))


class IO:
    @staticmethod
    def ouster(state: State, file, out_ls: PopList):
        metadata = client.SensorInfo(file.read())
        source = pcap.Pcap(state.args.input, metadata)
        Convertor.ouster_pcap_to_mxc(source, metadata, frame_ls=out_ls, N=state.args.N)


class Convertor:
    @staticmethod
    def ouster_pcap_to_mxc(source: client.PacketSource, metadata: client.SensorInfo, frame_ls: PopList, N: int = 1,
                           ) -> List[MatrixCloud]:
        # [doc-stag-pcap-to-csv]
        from itertools import islice
        # precompute xyzlut to save computation in a loop
        xyzlut = client.XYZLut(metadata)
        # create an iterator of LidarScans from pcap and bound it if num is specified
        scans = iter(client.Scans(source))
        if N:
            scans = islice(scans, N)
        for idx, scan in enumerate(scans):
            frame_ls.add(Cloud3dUtils.get_matrix_cloud(xyzlut, scan, Ch.channel_arr))
        return frame_ls


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
