import json
from threading import Event
from time import sleep
from typing import List, Tuple

from tools.pipes import RNode
from tools.structs import PopList
from utilities.utils import FileUtils, def_numpy, ArrayUtils, def_json, def_pcap

"""
@Module: ExportModule
@Description: Export point, predictions , statistics etc.
@Author: Radu Rebeja
"""
#####################
predictions = 'predictions'
points = 'points'
stats = 'stats'
data = 'data'
index = 'ix'
timestamp = 'timestamp'


#####################

class Routines(RNode):
    """
    Export routine
    """

    @classmethod
    def script(cls, parser) -> bool:
        parser.add_argument('--export', nargs='+', choices=[predictions, points, stats], help='Save results locally')
        return True

    def __init__(self, state):
        super().__init__(state)

    def dependencies(self):
        from streamprocessor.stream_process import Routines as processor
        from statistic.stats import Routines as statistic
        from OpenPCDet.tools.evaluate import Routines as detector
        return [processor, statistic, detector]

    def run(self, _input: List[PopList], output: PopList, **kwargs):
        export = {
            points: (self.read_list, 0),
            stats: (self.read_dict, 1),
            predictions: (self.read_dict, 2)
        }
        self.log.info(msg='Export:STARTED')
        FileUtils.Dir.mkdir_here(def_numpy)
        FileUtils.Dir.mkdir_here(def_json)
        while not _input[0].is_full():
            sleep(5)

        for arg in self.state.args.export:
            ls: list
            m, ix = export[arg]
            ls = m(_input[ix])
            with open('../resources/output/json/' + f'{arg}.json', 'w+') as x:
                json.dump(ls, x)
        self.log.info(msg='Export: done')

    def read_dict(self, in_ls: PopList):
        x = 0
        ls = []
        while not in_ls.full(x):
            ls.append({
                data: ArrayUtils.np_dict_to_list(in_ls.get(x, self.event)),
                index: x,
            })
            x += 1
        return ls

    def read_list(self, in_ls: PopList):
        x = 0
        ls = []
        while not in_ls.full(x):
            ls.append({
                data: in_ls.get(x, self.event).tolist(),
                index: x
            })
            x += 1
        return ls
