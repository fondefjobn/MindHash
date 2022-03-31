from typing import List, Optional, Union

from sensor.ouster_sensor import _IO, SensorParams
from tools.pipes import State, RoutineSet
from tools.structs.custom_structs import PopList
from utilities.utils import IO, FileUtils


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

    def UserInput(self, state: State, *args):
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
        with open(state.args.meta, 'r') as f:
            out_ls: PopList = args[1]
            getattr(IO, state.args.sensor)(state.args, f, out_ls)
            out_ls.set_full()
        Routines.logging.info(msg='UserInput reading: done')


default_sens_config = 'sensor/sensor_config.yaml'
default_stream_config = 'sensor/stream_config.yaml'


class SensorController:
    """SensorController"""

    def __init__(self, config: Optional[Union[dict, str]]):
        c_dict: dict
        if isinstance(config, str):
            c_dict = FileUtils.load_file(config, ext='yaml')
        else:
            c_dict = config
        self._io = _IO(SensorParams(c_dict))

    def start_stream(self):
        self._io.stream_scans()

    def stop_stream(self):
        pass

    def connect(self):
        pass
