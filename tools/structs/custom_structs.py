import dataclasses
from collections import deque
from threading import Event
from typing import List, Optional, Union, Tuple, TypeVar, Set, Iterable, Dict

import numpy as np
from numpy import ndarray
from wrapt import synchronized

"""
@Module: Custom Data Structures
@Description: Contains classes extending functionalities (Decorators) or offering new functionalities from scratch.
Also contains data classes.
@Author: Radu Rebeja
"""


class Index(int):
    def __new__(cls, val, *args, **kwargs):
        return super(cls, cls).__new__(cls, val)

    def __add__(self, other):
        res = super(Index, self).__add__(other)
        return self.__class__(res)


class PopList(dict):
    """
    PopList (PopularList) data struct
    List for concurrent writing and reading
    Uses Condition object for communication between threads
    (returned by PopList.sub())
    Lock is created within PopList
    For more details on Condition, Locks and Threads see:
    https://docs.python.org/3.8/library/threading.html#using-locks-conditions-and-semaphores-in-the-with-statement
    """
    _full_: bool
    _event_ls_: Set[Event]
    _func_: str = None
    _ID_ = None
    _T = TypeVar("_T")
    _KT = TypeVar("_KT")
    _VT = TypeVar("_VT")

    def __init__(self, seq: Optional[Union[Iterable[Tuple], Dict]] = None, doc: str = ''):
        prev = {} if seq is None else seq
        super().__init__(prev)
        self._full_ = False
        self._event_ls_ = set()
        self._len_ = len(prev)
        self.__doc__ += doc

    def append(self, __object: _T) -> None:
        """
          Appends an object to the list end and notifies all threads waiting on list update
          Parameters
          ----------
          __object

          Returns
          -------

          """
        self[len(self)] = __object
        self._notify_all()

    def qy(self, ix: int, event: Event) -> _T:
        """
        Appends threads Event object to waiting list if reached list end

        Parameters
        ----------
        ix
        event

        Returns
        -------

        """
        while ix not in self:
            self._event_ls_.add(event)
            event.wait()
            event.clear()
            self._event_ls_.remove(event)
        return self[ix]

    def full(self, i: int):
        """
        Checks if list is still updated
        Returns
        -------
    `   True - if list updating session finished
        """
        return i >= len(self) and self._full_

    def is_full(self):
        """
        Checks if list is still updated
        Returns
        -------
    `   True - if list updating session finished
        """
        return self._full_

    def set_full(self, b: bool = True):
        """
        Set full property
        Parameters
        ----------
        b: boolean for full-ness

        Returns
        -------

        """
        self._full_ = b
        if b:
            self._notify_all()

    def get_routine(self) -> str:
        return self._func_

    def clean(self, idxs: List[int]) -> None:
        [self.pop(ix, None) for ix in idxs]

    def __setitem__(self, k: _KT, v: _VT) -> None:
        super().__setitem__(k, v)
        self._len_ = self.__len__() + 1

    @synchronized
    def __len__(self):
        return self._len_

    def _notify_all(self):
        def notify(event: Event):
            event.set()

        list(map(notify, self._event_ls_.copy()))


class MatrixCloud:
    """Our project standardization data-structure for point clouds.
    All sensor outputs are converted to fit data into this class
    timestamps = array of float describing timestamp in UNIX epoch time
    clouds = [[X],[Y],[Z]] shaped matrix
    channels
    """

    def __init__(self):
        self.timestamps = None
        self.X: ndarray = None
        self.Y: ndarray = None
        self.Z: ndarray = None
        self.channels = {
            Ch.NEAR_IR: None,
            Ch.SIGNAL: None,
            Ch.REFLECTIVITY: None
        }
        self.LEN = 0


class Ch:
    RANGE = 'RANGE'
    NEAR_IR = 'NEAR_IR'
    REFLECTIVITY = 'REFLECTIVITY'
    SIGNAL = 'SIGNAL'
    channel_arr = [RANGE, SIGNAL, NEAR_IR, REFLECTIVITY]  # exact order of fields
