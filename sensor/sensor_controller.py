from math import inf
from typing import List, Optional, Union, Tuple

from sensor.sensor_set import __all__
from sensor.sensor_template import Sensor
from tools.pipeline import RNode
from tools.structs.custom_structs import PopList
from utilities.utils import FileUtils

"""
@Module: Sensor Controller
@Description: Tool for using 
See Also Architecture document on Pipelines
@Author: Radu Rebeja
"""

default_sens_config = 'sensor/config.yaml'
default_stream_config = 'sensor/config.yaml'


class SensorController(object):
    """SensorController
    Anything spicy you want to do with your sensor happens here
    e.g. settings """

    def __init__(self, config: Optional[Union[dict, str]], sensor: Sensor):
        c_dict: dict
        if isinstance(config, str):
            c_dict = FileUtils.load_file(config, ext='yaml')
        else:
            c_dict = config
        self.config = c_dict

    def start_stream(self):
        self._IO_.read()

    def stop_stream(self):
        pass

    def connect(self):
        pass


class Routines(RNode):
    """
    Main Sensor Input
    """

    @classmethod
    def script(cls, parser) -> bool:
        parser.add_argument('--n', type=int, default=None, help='Limit number N of processed frames')
        parser.add_argument('--sensor', default=None,
                            help='Sensor defining input type', choices=['ouster'], type=str.lower, required=True)
        parser.add_argument('--host', type=str, default=None, help='Sensor hostname')
        parser.add_argument('--port', type=int, default=None, help='Sensor port')
        parser.add_argument('--input', type=str, default=None, help='PCAP/other file for post-processing')
        parser.add_argument('--ext', type=str, default=None, help='File input extension')
        parser.add_argument('--meta', type=str, default=None, help='JSON metadata file for input file')
        parser.add_argument('--live',
                            help='Live-stream processing mode', action="store_true")
        return True

    def __init__(self, state):
        super().__init__(state)

    @RNode.assist
    def run(self, _input: List[PopList], output: PopList, **kwargs):
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
        sensor: Sensor = __all__[self.state.args.sensor](self.state.args, output, self.state.logger)  # SensorData here?
        # controller: SensorController = SensorController({}, sensor)
        if not self.state.args.live:
            sensor.convert()
        else:
            sensor.read()
        self.state.logger.info(msg='User input reading: DONE')

    def dependencies(self):
        return []

    channels: List[int] = [1, 2, 3, 4]

    def fconfig(self) -> str:
        pass

    def get_index(self) -> int:
        return inf
