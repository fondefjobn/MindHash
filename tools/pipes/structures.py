from argparse import Namespace
from abc import ABC, abstractmethod
from threading import Event
from typing import List

from numba import njit, jit

from tools.structs import PopList


class BundleDictionary(ABC):
    """
    Abstract class for shared states
    """

    @staticmethod
    def fid(p: property):
        return id(p)


class State:
    """
    Wrapper class for state and args used in script execution

    """
    state: dict
    args: Namespace

    def __init__(self, args: Namespace = None):
        self.state = {
            "success": True
        }
        self.args = args

    def merge(self, new_state):
        self.state.update(new_state.state)

    def __setitem__(self, key, value):
        self.state[key] = value

    def __getitem__(self, key):
        return self.state[key]


class RNode(object):
    """
    Parent class of routines acting as nodes in pipes.pipeline.PipelineDaemon
    Dependencies must be set by any class subclassing RNode
    """
    import logging
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    log = logging
    lspos = 2  # starting position for pop-list tuple

    def __init__(self, state):
        self.state = state
        self.event = Event()

    @classmethod
    def run_loop(cls, i: int, ixid: str):
        """
        Decorator function (for debugging only!)
        Additional loop functionality here - list clearing , closing ceremonies"""

        def loop(fnc):
            @njit
            def f(*args, **kwargs):
                kwargs[ixid] = i
                while not args[1][0].full(kwargs[ixid]):
                    fnc(*args, **kwargs)
                    kwargs[ixid] += 1
                args[2].set_full(True)

            return f

        return loop

    @classmethod
    def assist(cls, fnc):
        """
        For closing processes & logging
        """

        def f(*args, **kwargs):
            fnc(*args, **kwargs)
            args[2].set_full(True)  # verify this

        return f

    @abstractmethod
    def run(self, _input: List[list], output: list, **kwargs):
        pass

    @abstractmethod
    def dependencies(self) -> list:
        return []

    def h_dependencies(self) -> list:
        return list(map(hash, self.dependencies()))
