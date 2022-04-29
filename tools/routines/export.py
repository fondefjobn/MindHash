import json
from threading import Event
from time import sleep
from typing import List

from tools.pipes import RNode
from tools.structs import PopList
from utilities.utils import FileUtils, def_numpy, ArrayUtils

"""
@Module: ExportModule
@Description: Export point, predictions , statistics etc.
@Author: Radu Rebeja
"""


class Routines(RNode):
    """
    Export routine
    """
    def __init__(self, state):
        super().__init__(state)

    def run(self, _input: List[PopList], output: PopList, **kwargs):

        self.log.info(msg='Export:STARTED')

        FileUtils.Dir.mkdir_here(def_numpy)
        while not _input[0].is_full():
            sleep(5)

        for arg in self.state.args.export:
            ls: list
            if isinstance(_input[0][arg], dict):
                ls = self.read_dict(_input[0], arg)
            else:
                ls = self.read_list(_input[0], arg)
            with open('../resources/output/json/' + f'{arg}.json', 'w+') as x:
                json.dump(ls, x)
        self.log.info(msg='Export: done')

    def dependencies(self):
        from streamprocessor.stream_process import Routines as processor
        from statistic.stats import Routines as stats
        from OpenPCDet.tools.evaluate import Routines as detector
        return [processor, stats, detector]

    def read_dict(self, in_ls, arg):
        x = 0
        ls = []
        while not in_ls.full(x):
            in_ls[x][arg] = ArrayUtils.np_dict_to_list(in_ls[x][arg])
            ls.append({arg: in_ls[x][arg]})
            x += 1
        return ls

    def read_list(self, in_ls, arg):
        x = 0
        ls = []
        while not in_ls.full(x):
            in_ls[x][arg] = in_ls[x][arg].tolist()
            ls.append({arg: in_ls[x][arg]})
            x += 1
        return ls
