from collections import deque
from threading import Event
from typing import List, Optional, Union, Tuple, TypeVar, Set

from numpy import ndarray

"""
@Module: Custom Data Structures
@Description: Contains classes extending functionalities (Decorators) or offering new functionalities from scratch.
Also contains data classes.
@Author: Radu Rebeja
"""


class PopList(deque):
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

    def __init__(self, seq: Optional[Union[Tuple, List]] = None, doc: str = ''):
        prev = [] if seq is None else seq
        super().__init__(prev)
        self._full_ = False
        self._event_ls_ = set()
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
        super().append(__object)
        self._notify_all()

    def get(self, ix: int, event: Event) -> _T:
        """
        Appends threads Event object to waiting list if reached list end

        Parameters
        ----------
        ix
        event

        Returns
        -------

        """
        while ix == len(self):
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
