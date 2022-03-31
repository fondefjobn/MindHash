from threading import Event

from tools.pipes import RoutineSet, State
from utilities.utils import FileUtils, def_numpy


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
        Routines.logging.info(msg='Export:STARTED')
        x = 0
        e = Event()
        in_ls = args[0]
        FileUtils.Dir.mkdir_here(def_numpy)
        while x < len(in_ls) or not in_ls.full():
            out = in_ls.get(x, e)
            FileUtils.Output.to_numpy(out, def_numpy, str(x))
            x += 1
        Routines.logging.info(msg='Export: done')
