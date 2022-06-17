from abc import ABC, abstractmethod
from argparse import Namespace
from dataclasses import dataclass
from typing import Dict, List, Tuple
from tools.pipeline.structures import RNode

"""
    Generates ordered list of all routines that may be part of the pipeline
    Tuple associates a key from CLI argparse with a routine
    If a routine existence is required, use anything as key except None

    Dict[Arg/Any | Routine]
"""


@dataclass(frozen=True)
class RoutineSet(ABC):

    @abstractmethod
    def activationList(self, a: Namespace) -> List[Tuple[object, RNode]]:
        return []

    @abstractmethod
    def __all__(self) -> set:
        return set()


def __generate_list__(state, __all__: List[Tuple[object, RNode]]) -> Dict[int, RNode]:
    return dict([(hash(y), y(state)) for (x, y) in __all__ if x not in (False, None)])
