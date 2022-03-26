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


    Note: Must be used only within Context Manager
    (with statement) of the PopList instance's Condition object
    Note: Not yet tested
    """
    __full__: bool
    __event_ls__: Set[Event]
    _T = TypeVar("_T")

    def __init__(self, seq: Optional[Union[Tuple, List]] = None):
        prev = [] if seq is None else seq
        super().__init__(prev)
        self.__full__ = False
        self.__event_ls__ = set(prev)
        self.event_dict = {}

    def add(self, __object: _T) -> None:
        self.append(__object)
        self.notify_all()

    def get(self, ix: int, e: Event = None):
        while ix == len(self):
            self.__event_ls__.add(e)
            e.wait()
            e.clear()
            self.__event_ls__.remove(e)
        return self[ix]

    @synchronized
    def full(self):
        """
        Checks if list is still updated
        Returns
        -------
    `   True if list updating session finished
        """
        return self.__full__

    @synchronized
    def set_full(self, b: bool):
        """
        Set full property
        Parameters
        ----------
        b: boolean for full-ness

        Returns
        -------

        """
        self.__full__ = b
        if b:
            self.notify_all()

    @synchronized
    def sub(self):
        """Subscribe a thread by returning condition variable to list updates"""
        return self.__event_ls__

    def notify_all(self):
        def notify(event: Event):
            event.set()
        map(notify, self.__event_ls__)
