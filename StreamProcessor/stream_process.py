from threading import Event
from queue import Queue

from tools.pipes import RoutineSet, State
from tools.structs.custom_structs import PopList
from utilities.utils import FileUtils as Fs, \
    Cloud3dUtils


class ConfigMap:
    """"""
    rate = 'sample_rate'
    q_size = 'queue_size'
    timer = 'timer'
    t_end = 'timer_stop'
    sl = 'local_saves'
    lp = 'local_path'
    live = 'livestream'


"""Aliases & Global values"""
################
Cm = ConfigMap
Q = Queue


################

class Routines(RoutineSet):

    def id(self):
        return 'PROCESS_BUNDLE'

    def ListProcessor(self, state: State, *args): #abstract to methods
        in_ls: PopList = args[0]
        out_ls: PopList = args[1]
        sp: StreamProcessor = StreamProcessor(in_ls, out_ls)
        x = 0
        e = Event()
        while x < len(in_ls) or not in_ls.full():
            out = in_ls.get(x, e)
            sp.read_stream(out)
            x += 1
        out_ls.set_full()
        Routines.logging.info(msg='ListProcessor: done')


class StreamProcessor:
    config: dict = None
    idle: bool = False
    in_ls: PopList
    out_ls: PopList

    def __init__(self, in_ls: PopList, out_ls: PopList, cfg_path=None):
        self.in_ls = in_ls
        self.out_ls = out_ls
        # self._load_config(cfg_path)

    def _load_config(self, cfg_path):
        self.config = Fs.parse_yaml(cfg_path)

    def read_stream(self, mx):
        self.out_ls.add(Cloud3dUtils.to_pcdet(mx))
