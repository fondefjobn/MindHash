import json
from threading import Event
from time import sleep

from tools.pipes import RoutineSet, State
from utilities.utils import FileUtils, def_numpy, ArrayUtils


class Routines(RoutineSet):

    def id(self):
        return 'UTILS_BUNDLE'

    def ExportLocal(self, state: State, *args):
        """
         Routine: Export conversion results

         Produces: None

         Consumes: PcapList

         Requires: None
         """
        self.log.info(msg='Export:STARTED')

        in_ls = args[0]
        FileUtils.Dir.mkdir_here(def_numpy)
        while not in_ls.is_full():
            sleep(5)

        for arg in state.args.export:
            ls:list
            if isinstance(in_ls[0][arg], dict):
                ls = self.read_dict(in_ls, arg)
            else:
                ls = self.read_list(in_ls, arg)
            with open('../resources/output/json/' + f'{arg}.json', 'w+') as x:
                json.dump(ls, x)
            # FileUtils.Output.to_numpy(out, def_numpy, str(x))
        self.log.info(msg='Export: done')

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
