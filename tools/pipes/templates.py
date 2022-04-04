from argparse import Namespace
from abc import ABC, abstractmethod
from threading import Event

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


class RoutineSet(object):
    """
    Wrapper class for bundles of routines.
    ID must be set by any class subclassing RoutineSet
    and added to pipeline config file accordingly
    """
    import logging
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    log = logging
    lspos = 2  # starting position for pop-list tuple

    def __init__(self):
        self.event = Event()

    @classmethod
    def poplist_loop(cls, arg: int, ix: str):
        """
        Decorator function

        Additional loop functionality here - list clearing , closing ceremonies"""

        def loop(fnc):
            def f(*args):
                st = 1
                ls = 2 + arg
                args[st][ix] = 0
                while not args[ls].full(args[st][ix]):
                    fnc(*args)
                    args[st][ix] += 1
                args[ls].set_full(True)

            return f

        return loop

    @classmethod
    def full(cls, fnc):
        def f(*args):
            ls: PopList = fnc(*args)
            print(ls, 'setting true')

            ls.set_full(True)

        return f

    @abstractmethod
    def id(self):
        return None
