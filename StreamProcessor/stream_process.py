from threading import Thread
from queue import Queue

from tools.pipes.p_tmpl import Pipeline, GlobalDictionary
from utilities.custom_structs import PopList
from utilities.utils import FileUtils as Fs, \
    MatrixCloud as MxCloud, Cloud3dUtils
from numpy import ndarray


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
Gb = GlobalDictionary


################

class QueueProcessor(Pipeline):

    def run(self):
        super().run()
        pcap_ls: PopList = self.state[Gb.PcapList]
        print("Started")
        x = 0
        while x < 10:
            out = pcap_ls.get(x, self.event)
            x += 1


class ProcessThread(Thread):
    in_queue: "Q[MxCloud]"
    out_queue: "Q[ndarray]"

    def __init__(self, q: "Q[MxCloud]", conf: dict):
        super().__init__()
        self.config = conf
        self.in_queue = q
        self.out_queue = Q(maxsize=self.config[Cm.q_size])

    def _setup(self):
        pass

    def run(self) -> None:
        c = self.config
        timeout = 10 if [Cm.live] else -1  # wrong

    def _read(self):
        while True:
            o = Cloud3dUtils.to_pcdet(self.in_queue.get(block=True, timeout=10))
            self.out_queue.put(o, block=True)


class StreamProcessor:
    config: dict = None
    idle: bool = False
    process: ProcessThread = None
    in_queue: "Q[MxCloud]"
    out_queue: "Q[ndarray]"

    def __init__(self, queue: "Q[MxCloud]", cfg_path):
        self.in_queue = queue
        self._load_config(cfg_path)

    def _load_config(self, cfg_path):
        self.config = Fs.parse_yaml(cfg_path)

    def read_stream(self):
        self.process = ProcessThread(self.in_queue, self.config)
        self.out_queue = self.process.out_queue
        self.process.start()

    def stop_stream(self):
        self.process.join()
