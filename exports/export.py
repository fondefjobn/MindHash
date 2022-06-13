import json
from threading import Event
from time import sleep
from typing import List, Tuple

from tools.pipeline import RNode
from tools.structs import PopList, Index
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

    def fconfig(self):
        return None

    ix: int = 0

    def get_index(self) -> int:
        return self.ix

    @classmethod
    def script(cls, parser) -> bool:
        parser.add_argument('--export', nargs='+', choices=[predictions, points, stats], help='Save results locally')
        return True

    def __init__(self, state):
        super().__init__(state)

    def dependencies(self):
        from streamprocessor.stream_process import Routines as processor
        from statistic.stats import Routines as statistic
        from OpenPCDet.tools.detection import Routines as detector
        return [processor, statistic, detector]

    @RNode.assist
    def run(self, _input: List[PopList], output: PopList, **kwargs):
        log = self.state.logger
        export = {
            points: (self.read_list, 0),
            stats: (self.read_dict, 1),
            predictions: (self.read_dict, 2)
        }
        log.info(msg='Export: STARTED')
        FileUtils.Dir.mkdir_here(def_numpy)
        FileUtils.Dir.mkdir_here(def_json)
        _input[0].qy(0, self.event)
        while not _input[0].full(self.ix):
            for arg in self.state.args.export:
                ls: list
                m, ix = export[arg]
                ls = m(_input[ix])  # TODO change to multithread ?
                with open('../resources/output/json/' + f'{arg}.json', 'w+') as x:
                    json.dump(ls, x)

        log.info(msg='Export: DONE')

    def read_dict(self, in_ls: PopList):
        ls = []
        while not in_ls.full(self.ix):
            ls.append({
                data: ArrayUtils.np_dict_to_list(in_ls.qy(self.ix, self.event)),
                index: self.ix,
            })
            self.ix += 1
        self.ix = 0
        return ls

    def read_list(self, in_ls: PopList):
        ls = []
        while not in_ls.full(self.ix):
            ls.append({
                data: in_ls.qy(self.ix, self.event).tolist(),
                index: self.ix
            })
            self.ix += 1
        self.ix = 0
        return ls
