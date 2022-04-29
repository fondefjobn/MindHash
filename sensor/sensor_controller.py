from typing import List, Optional, Union

from sensor.sensor_set import __all__
from sensor.sensor_template import Sensor
from tools.pipes import RNode
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
        sensor: Sensor = __all__[self.state.args.sensor](self.state.args, output)
        controller: SensorController = SensorController({}, sensor)
        if not self.state.args.live:
            sensor.convert()
        else:
            sensor.read()
        Routines.log.info(msg='UserInput reading: done')
        return output

    def dependencies(self):
        return []

    channels: List[int] = [1, 2, 3, 4]
