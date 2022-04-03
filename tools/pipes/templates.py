from argparse import Namespace
from abc import ABC, abstractmethod

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

    @abstractmethod
    def id(self):
        return None
