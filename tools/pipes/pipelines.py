import threading
from threading import Thread
from typing import List, Dict, Tuple

from easydict import EasyDict

from tools.pipes.structures import RNode, State
from tools.structs import PopList
from utilities.utils import FileUtils as fu

"""
@Module: Pipelines
@Description: Simple tool for building and execution of multithreading routines within a chained pipeline
Chaining is achieved with IO PopLists that routines share for parallel list processing. 
See Also Architecture document on Pipelines
@Author: Radu Rebeja
"""

# Dictionary of string values
CONFIG: str = '../tools/pipes/config.yaml'
inputs: str = 'PRODUCER'
output: str = 'output'
_exec: str = 'exec'
_mt: str = 'mt'

"""
    Generates ordered list of all routines that may be part of the pipeline
    Tuple associates a key from CLI argparse with a routine
    If a routine existence is required, use anything as key except None

    Dict[Arg/Any | Routine]
"""


class PipelineDaemon:
    pipeline: List[Thread] = []

    def execute_pipeline(self):
        """
        Iterate over all routines and execute all.
        Blocking routines do not use multiprocessing (multithreading)
        Non-Blocking create a separate process with multiprocessing lib
        The state is shared by routines but usage should be limited to debugging! (except state.args)
        Returns
        -------

        """
        for ix, pl in enumerate(self.pipeline):
            pl.start()

    def build_pipeline(self, state: State):
        """
            Builds pipeline by iterating over the list of PopList dict objects in
            the configuration dictionary. Updates at each step the pipeline chain
            Parameters
            ----------
            bundles list of available bundles
            state shared state containing execution arguments and values
            Returns list of threads (not started)
            -------

            """
        from tools.pipes.routines import __generate_list__, RoutineSet
        from tools.pipes.structures import RNode
        list(map(lambda x: x.script(state.parser), RoutineSet.__all__))
        state.parse_args()
        routines: Dict[int, RNode] = __generate_list__(state, state.args)
        bundle_list = routines.items()
        threads: dict = {}
        for (_hash, rt) in bundle_list:
            if not isinstance(rt, RNode):
                raise IOError('Found invalid routine object')
            if rt.__class__ not in RoutineSet.__all__:
                raise AssertionError(f'{rt} : Not present in list of accepted node routines')
        self.update(routines, threads, routines.popitem())
        self.pipeline = [threading.Thread(target=r[_exec], args=(r[inputs], r[output]))
                         for r in threads.values()]

    def update(self, routines: Dict[int, RNode], threads: dict, rt: Tuple[int, RNode], cycles=False):
        p: PopList = PopList()
        if rt[0] in threads and not cycles:
            raise Exception('Detected cycle in ' + f'{rt[1]}: Cycles are prohibited')
        if rt[1] is not None:
            threads[rt[0]] = {
                _exec: rt[1].run,
                inputs: rt[1].dependencies(),
                output: p,
                _mt: True
            }
            routines.pop(rt[0], None)
            if not rt[1].dependencies() == []:
                for ix, parent in enumerate(rt[1].h_dependencies()):
                    if parent in threads:
                        threads[rt[0]][inputs][ix] = threads[parent][output]
                    else:
                        if routines.get(parent) is not None:
                            self.update(routines, threads, rt=(parent, routines.get(parent)), cycles=cycles)
                            threads[rt[0]][inputs][ix] = threads[parent][output]
        if len(routines) != 0:
            self.update(routines, threads, routines.popitem(), cycles=cycles)
