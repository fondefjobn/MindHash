import dataclasses
import functools
import os
from abc import ABC, abstractmethod
from argparse import Namespace, ArgumentParser
from pathlib import Path
from threading import Event
from typing import List

from easydict import EasyDict

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

    def load_config(self, __file__: str, fname: str = None):
        load_cfg: str
        if fname is not None:
            load_cfg = fname
        elif self.fconfig() is not None:
            load_cfg = self.fconfig()
        else:
            raise IOError(f"Missing available config in: {__file__}")
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), Path(load_cfg))
        self.config = EasyDict(FileUtils.parse_yaml(str(path)))

    def compose(self, struct: object):
        pass

    @classmethod
    def check_completion(cls, ls: List[PopList]):
        ls = [x.is_full() for x in ls]
        pred = lambda x: x is True
        return functools.reduce(lambda x, y: x and pred(y), ls,
                                True)

    @abstractmethod
    def fconfig(self) -> str:
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
    def run(self, _input: List[PopList], output: PopList, **kwargs):
        """

        Parameters
        ----------
        _input : List of PopLists as requested respecting order specified in dependencies()
        output : PopList used for outputting results or None if output is
        kwargs :

        Returns
        -------

        """
        pass

    @abstractmethod
    def dependencies(self) -> list:
        """
        Returns
        -------
        List of RNode subclasses (non-instances) required by your RNode
        Note: Said dependencies may not be instantiated depending on the script
        arguments. Subclass implementation must handle such cases.
        """
        return []

    @abstractmethod
    def get_index(self) -> int:
        """

        Returns
        -------

        Return the node's processing index (step, stage, phase) describing
        task progress on shared data. Subclasses implement this method with
        a private index variable.
        """
        return -1

    @abstractmethod
    def script(self, parser: ArgumentParser) -> bool:
        """
        Append script arguments to the argument parser
        Return True if said arguments
        """
        return False

    def h_dependencies(self) -> list:
        return list(map(hash, self.dependencies()))


class MissingDataclassFieldError(Exception):  # refactor to custom errors
    pass


@dataclasses.dataclass
class DClass:
    @classmethod
    def check_missing(cls, ds):
        try:
            cls_fields = dataclasses.fields(ds)
            for field in cls_fields:
                if field in (dataclasses.MISSING, None):
                    raise MissingDataclassFieldError(f"{field} Not supplied in {ds}")
        except IOError('Supplying non-dataclass instance to field checking method'):
            raise


@dataclasses.dataclass
class ThreadData:
    """
    Dataclass ThreadData - used for pipeline construction
    and strongly typed value storing
    """
    routine: RNode
    exec: object
    inputs: list
    output: PopList
    mt: bool
