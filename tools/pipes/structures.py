import dataclasses
import os
from abc import ABC, abstractmethod
from argparse import Namespace, ArgumentParser
from pathlib import Path
from threading import Event
from typing import List

from easydict import EasyDict
from numba import njit

from tools.structs import PopList
from utilities.utils import FileUtils


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
    parser: ArgumentParser
    logger = None

    def __init__(self, parser: ArgumentParser = None):
        self.state = {  # for debugging only
            "success": True
        }
        self.parser = parser

    def merge(self, new_state):
        self.state.update(new_state.state)

    def parse_args(self):
        self.args = self.parser.parse_args()

    def __setitem__(self, key, value):
        self.state[key] = value

    def __getitem__(self, key):
        return self.state[key]


class RModule(object):
    config: EasyDict = None

    def __init__(self):
        pass

    def generate_steps(self):
        pass

    def load_config(self, __file__):
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), Path(self.fconfig()))
        self.config = EasyDict(FileUtils.parse_yaml(str(path)))

    def compose(self, struct: object):
        pass

    @abstractmethod
    def fconfig(self):
        return None


class RNode(RModule):
    """
    Parent class of routines acting as nodes in pipes.pipeline.PipelineDaemon
    Dependencies must be set by any class subclassing RNode
    """

    def __init__(self, state):
        super().__init__()
        self.state = state
        self.event = Event()

    @classmethod
    def run_loop(cls, i: int, ixid: str):
        """
        Decorator function (for debugging only!)
        Additional loop functionality here - list clearing , closing ceremonies"""

        def loop(fnc):
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
        """
        Return RNode subclasses (non-instances) required by your RNode
        """
        return []

    @abstractmethod
    def get_index(self) -> int:
        return None

    @abstractmethod
    def script(self, parser) -> bool:
        return False

    def h_dependencies(self) -> list:
        return list(map(hash, self.dependencies()))


@dataclasses.dataclass
class ThreadData:
    routine: RNode
    exec: object
    inputs: list
    output: PopList
    mt: bool
