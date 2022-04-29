import threading
from threading import Thread
from typing import List, Dict, Tuple

from easydict import EasyDict

from tools.pipes.structures import RNode
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
PRODUCER: str = 'PRODUCER'
CONSUMER: str = 'CONSUMER'
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

    def update_routines(self, bundles: dict, schema: dict, ls_cfg, role: str, pop_ls: PopList):
        """
        v.1
        Initialize missing routines from the list and update Producers and Consumers
        for present instances by assigning either an Input or Output list.
        Parameters
        ----------
        pop_ls
        role
        schema
        bundles
        ls_cfg

        Returns
        -------

        """

        def update(obj_cfg):
            if obj_cfg.ID not in schema:
                if obj_cfg.BUNDLE not in bundles:
                    return False
                else:
                    schema[obj_cfg.ID] = {
                        _exec: getattr(bundles[obj_cfg.BUNDLE], obj_cfg.ID),
                        PRODUCER: None,
                        CONSUMER: None,
                        _mt: obj_cfg.MT
                    }
            schema[obj_cfg.ID][role] = pop_ls
            return True

        list(map(update, ls_cfg))

    def build_pipeline(self, state):
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
        print(routines)
        print(threads)

    def update(self, routines: Dict[int, RNode], threads: dict, rt: Tuple[int, RNode], cycles=False):
        p: PopList = PopList()
        print(routines)
        if rt[0] not in threads:
            threads[rt[0]] = {
                _exec: rt[1].run,
                inputs: rt[1].dependencies(),
                output: p,
                _mt: True
            }
        else:
            if not cycles:
                raise Exception('Detected cycle in ' + f'{rt[1]}: Cycles are prohibited')
        routines.pop(rt[0], None)
        if not rt[1].dependencies() == []:
            for ix, parent in enumerate(rt[1].h_dependencies()):
                if parent in threads:
                    threads[rt[0]][inputs][ix] = threads[parent][output]
                else:
                    print('RECURSION')
                    self.update(routines, threads, rt=(parent, routines.get(parent)), cycles=cycles)
                    threads[rt[0]][inputs][ix] = threads[parent][output]
        if len(routines) != 0:
            self.update(routines, threads, routines.popitem(), cycles=cycles)
