import threading
from typing import List, Optional, Union, Tuple, TypeVar, Set
from threading import Event

from numpy import iterable
from wrapt import synchronized

"""
Module for custom data structs
"""


class PopList(List):
    """
    PopList (PopularList) data struct
    List for concurrent writing and reading
    Uses Condition object for communication between threads
    (returned by PopList.sub())
    Lock is created within PopList
    For more details on Condition, Locks and Threads see:
    https://docs.python.org/3.8/library/threading.html#using-locks-conditions-and-semaphores-in-the-with-statement

    Note: Not yet tested
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

    def add(self, __object: _T) -> None:
        """
        Appends an object to the list end and notifies all threads waiting on list update
        Parameters
        ----------
        __object

        Returns
        -------

        """
        self.append(__object)
        self._notify_all()

    def get(self, ix: int, e: Event = None) -> _T:
        """
        Appends threads Event object to waiting list if reached list end

        Parameters
        ----------
        ix
        e

        Returns
        -------

        """
        while ix == len(self):
            self._event_ls_.add(e)
            e.wait()
            e.clear()
            self._event_ls_.remove(e)
        return self[ix]

    @synchronized
    def full(self):
        """
        Checks if list is still updated
        Returns
        -------
    `   True if list updating session finished
        """
        return self._full_

    @synchronized
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
