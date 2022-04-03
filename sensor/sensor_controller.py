from argparse import Namespace
from typing import List, Optional, Union

from ouster import client, pcap

from sensor.ouster_sensor import _IO_, SensorParams
from tools.pipes import State, RoutineSet
from tools.structs.custom_structs import PopList, MatrixCloud, Ch
from utilities.utils import FileUtils, Cloud3dUtils

"""
@Module: Sensor Controller
@Description: Tool for using 
See Also Architecture document on Pipelines
@Author: Radu Rebeja
"""


class Routines(RoutineSet):

    def id(self):
        return "SENSOR_BUNDLE"

    channels: List[int] = [1, 2, 3, 4]

    def LiveStream(self, state: State, *args):  # to be deprecated in favor of united method for any input
        out_ls = args[1]
        params = {
            "hostname": state.args.host,
            "lidar_port": state.args.port,
            "imu_port": 7503,
            "sample_rate": 0,
            "output": out_ls
        }
        controller = SensorController(params)
        controller.start_stream()

    def user_input(self, state: State, *args):
        """
        Routine: User Input File post-process

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
        if not state.args.live:
            with open(state.args.meta, 'r') as f:
                out_ls: PopList = args[1]
                getattr(IO, state.args.sensor)(state.args, f, out_ls)
                out_ls.set_full()
            Routines.logging.info(msg='UserInput reading: done')
        else:
            self.LiveStream(state, args)


default_sens_config = 'sensor/sensor_config.yaml'
default_stream_config = 'sensor/config.yaml'


class SensorController(IO):
    """SensorController"""

    def __init__(self, config: Optional[Union[dict, str]]):
        c_dict: dict
        if isinstance(config, str):
            c_dict = FileUtils.load_file(config, ext='yaml')
        else:
            c_dict = config
        self._io = _IO_(SensorParams(c_dict))  # apply reflectance on ouster IO

    def start_stream(self):
        self._io.stream_scans()

    def stop_stream(self):
        pass

    def connect(self):
        pass





class Convertor:
    """

    """

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
