import os
import random
from ouster import client as cl
import yaml
from typing import List
from yaml import SafeLoader
import numpy as np
from ouster import client, pcap

def_numpy: str = 'output/numpy'
def_json: str = 'output/json'
def_pcap: str = 'output/pcap_out'

"""
Utilities Module
if classes become bloated we split per module
"""


class Ch:
    RANGE = 'RANGE'
    NEAR_IR = 'NEAR_IR'
    REFLECTIVITY = 'REFLECTIVITY'
    SIGNAL = 'SIGNAL'
    XYZ = 'XYZ'
    channel_arr = [RANGE, SIGNAL, NEAR_IR, REFLECTIVITY]  # exact order of fields


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
    def safeParsing(path: str, parse_f, out=None, *args, **kwargs):
        try:
            with open(path) as f:
                if out is not None:
                    return FileUtils.__parse(parse_f(f, *args, **kwargs), out)
                else:
                    return parse_f(f, *args, **kwargs)
        except (OSError, yaml.YAMLError):
            return None

    @staticmethod
    def parseYaml(path: str, output=None):
        return FileUtils.safeParsing(path, yaml.load, out=output, Loader=SafeLoader)

    class Output:
        """Convert objects and save in specified file format"""

        # random file output names
        a: int = 2 ** 5
        b: int = a ** 2

        @staticmethod
        def to_numpy(o: np.ndarray, path: str, name: str = str(random.randint(a, b)), sep='/'):
            FileUtils.Dir.mkdir_here(path)

            np.save(os.path.join(path, name), o)

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
        #  x, y, z =
        field_names = channel_arr

        # use integer mm to avoid loss of precision casting timestamps
        xyz = (xyzlut(scan) * 1000).astype(np.int64)

        for ix, ch in enumerate(scan.fields):
            f = scan.field(ch)
            print(len(f))
            matrix_cloud.channels[field_names[ix]] = f
        x, y, z = [c.flatten() for c in np.dsplit(xyz, 3)]
        matrix_cloud.clouds[Ch.XYZ] = [x, y, z]
        return matrix_cloud

    @staticmethod
    def to_pcdet(matrix_cloud: MatrixCloud, path: str = None):
        # only store return signal intensity
        field_vals = matrix_cloud.channels[Ch.SIGNAL]
        field_vals = ArrayUtils.norm_zero_one(field_vals)
        # get all data as one H x W x n (inputs) int64 array
        x = matrix_cloud.clouds[Ch.XYZ][0]
        y = matrix_cloud.clouds[Ch.XYZ][1]
        z = matrix_cloud.clouds[Ch.XYZ][2]
        frame = np.array([x, y, z, np.zeros(x.shape[0])])

        # frame = client.destagger(metadata, frame)  # verify de-stagger
        # frame.reshape(-1, frame.shape[2])  # verify change
        # print(frame.shape)
        if path is None:
            return frame
        FileUtils.Output.to_numpy(frame, path)


class ArrayUtils:

    @staticmethod
    def norm_zero_one(data: np.ndarray):
        """Normalize array values to [0,1]"""
        return (data - np.min(data)) / (np.max(data) - np.min(data))


class PcapUtils:
    @staticmethod
    def pcap_to_pcdet(source: client.PacketSource,
                      metadata: client.SensorInfo,
                      num: int = 0,
                      npy_dir: str = ".",
                      npy_base: str = "pcap_out",
                      npy_ext: str = "npy") -> None:

        # [doc-stag-pcap-to-csv]
        from itertools import islice
        # precompute xyzlut to save computation in a loop
        xyzlut = client.XYZLut(metadata)

        # create an iterator of LidarScans from pcap and bound it if num is specified
        scans = iter(client.Scans(source))
        if num:
            scans = islice(scans, num)

        for idx, scan in enumerate(scans):
            # copy per-column timestamps for each channel
            matrix_cloud = Cloud3dUtils.get_matrix_cloud(xyzlut, scan, Ch.channel_arr)
            Cloud3dUtils.to_pcdet(matrix_cloud)


def pcap_to_npy(source: client.PacketSource,
                metadata: client.SensorInfo,
                num: int = 0):
    PcapUtils.pcap_to_pcdet(source, metadata, num)


parserMap = {
    'yaml': FileUtils.parseYaml,
    'csv': None,
    'las': None,
    'json': None,

}

outputMap = {
    'numpy': FileUtils.Output.to_numpy,
    'json': FileUtils.Output.to_json
}


def main():
    with open('../pcaps/OS1-32BH_sample.json', 'r') as f:
        metadata = client.SensorInfo(f.read())
    source = pcap.Pcap('../pcaps/OS1-32BH_fw2-1_sampledata.pcap', metadata)

    PcapUtils.pcap_to_pcdet(source, metadata, num=1)


if __name__ == "__main__":
    main()
