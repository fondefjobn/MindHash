from argparse import Namespace
from typing import List, Optional, Union

from ouster import client, pcap

from sensor.sensor_template import Sensor
from sensor.sensor_set import __all__
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

    @RoutineSet.full
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
        out_ls: PopList = args[1]
        sensor: Sensor = __all__[state.args.sensor](state.args, out_ls)
        if not state.args.live:
            sensor.convert()
        else:
            sensor.read()
        Routines.log.info(msg='UserInput reading: done')
        return out_ls


default_sens_config = 'sensor/config.yaml'
default_stream_config = 'sensor/config.yaml'


class SensorController(object):
    """SensorController
    Anything spicy you want to do with your sensor happens here"""

    def __init__(self, config: Optional[Union[dict, str]], sensor: Sensor):
        c_dict: dict
        if isinstance(config, str):
            c_dict = FileUtils.load_file(config, ext='yaml')
        else:
            c_dict = config

    def start_stream(self):
        self._IO_.read()

    def stop_stream(self):
        pass

    def connect(self):
        pass
