import logging
import sys
import threading
from abc import ABC
from math import inf
from threading import Thread
from time import sleep
from typing import List, Dict, Tuple

import schedule
from pcdet.utils import common_utils
from schedule import repeat, run_pending, every
from tools.pipes.structures import RNode, State, ThreadData, RModule
from tools.structs import PopList

"""
@Module: Pipelines
@Description: Simple tool for building and execution of multithreading routines within a chained pipeline
Chaining is achieved with IO PopLists that routines share for parallel list processing. 
See Also Architecture document on Pipelines
@Author: Radu Rebeja
"""

# Dictionary of string values
CONFIG: str = '../tools/pipes/config.yaml'
_inputs_: str = 'PRODUCER'
_output_: str = 'output'
_exec_: str = 'exec'
_mt_: str = 'mt'
_routine_: str = 'routine'

"""
    Generates ordered list of all routines that may be part of the pipeline
    Tuple associates a key from CLI argparse with a routine
    If a routine existence is required, use anything as key except None

    Dict[Arg/Any | Routine]
"""

logger = common_utils.create_logger()


class PlineMod(RModule, ABC):
    lists: List[PopList]
    delay: int = 0
    terminate: bool = False

    def __init__(self):
        super().__init__()
        self.lists = []

    def __cache_clean__(self, routines: Dict[int, ThreadData] = None):
        min_index: int = sys.maxsize
        if routines is not None:
            for rt in routines.values():
                ix = rt.routine.get_index()
                min_index = ix if ix < min_index else min_index
            if min_index > self.delay:
                clean_ls: List[int] = list(range(self.delay, min_index))
                for ls in self.lists:
                    if len(ls) != 0:
                        ls.clean(clean_ls)
                print(self.delay, min_index)
                self.delay = min_index
                logger.info(msg="Cache cleaning iteration completed", )
            else:
                self.terminate = True

    def manage_mem(self, routines: Dict[int, dict]):
        schedule.every(10).seconds.do(self.__cache_clean__, routines=routines)
        while not self.terminate:
            run_pending()
            sleep(1)
        logger.info("Cache management finished")


class Pipeline(PlineMod):
    pipeline: List[Thread]

    routines: Dict[int, dict]

    def __init__(self):
        super().__init__()
        self.pipeline = []
        self.routines = []

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
        super().manage_mem(self.routines)
        if self.terminate:
            [t.join(0) for t in self.pipeline]  # only necessary if threads are stuck
            logger.info(msg="All threads joined.")
        logger.info(msg="Pipeline routine execution completed. Exiting.")

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

        # collect script args & parse
        list(map(lambda x: x.script(state.parser), RoutineSet.__all__))
        state.parse_args()
        state.logger = logger

        # generate active routine set using args
        routines: Dict[int, RNode] = __generate_list__(state, state.args)

        # verify routines
        bundle_list = routines.items()
        threads: Dict[int, ThreadData] = {}
        for (_hash, rt) in bundle_list:
            if not isinstance(rt, RNode):
                raise IOError('Found invalid routine object')
            if rt.__class__ not in RoutineSet.__all__:
                raise AssertionError(f'{rt} : Not present in list of accepted node routines')

        # initialize recursive building & build the thread list
        self.update(routines, threads, routines.popitem())
        self.pipeline = [threading.Thread(target=r.exec, args=(r.inputs, r.output))
                         for r in threads.values()]
        self.routines = threads

    def update(self, routines: Dict[int, RNode], threads: Dict[int, ThreadData], rt: Tuple[int, RNode], cycles=False):
        p: PopList = PopList()
        if rt[0] in threads and not cycles:
            raise Exception('Detected cycle in ' + f'{rt[1]}: Cycles are prohibited')
        if rt[1] is not None:
            threads[rt[0]] = ThreadData(rt[1], rt[1].run, rt[1].dependencies(), p, True)
            self.lists.append(p)
            routines.pop(rt[0], None)
            if not rt[1].dependencies() == []:
                for ix, parent in enumerate(rt[1].h_dependencies()):
                    if parent in threads:
                        threads[rt[0]].inputs[ix] = threads[parent].output
                    else:
                        if routines.get(parent) is not None:
                            self.update(routines, threads, rt=(parent, routines.get(parent)), cycles=cycles)
                            threads[rt[0]].inputs[ix] = threads[parent].output
        if len(routines) != 0:
            self.update(routines, threads, routines.popitem(), cycles=cycles)

    def fconfig(self):
        return None
