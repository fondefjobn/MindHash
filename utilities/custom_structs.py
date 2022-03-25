import threading
from typing import List, Optional, Union, Tuple, TypeVar
from threading import Thread, Condition

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
    __cond__: Condition
    _T = TypeVar("_T")

    def __init__(self, seq: Optional[Tuple, List] = None):
        prev = [] if seq is None else seq
        super().__init__(prev)
        self.__full__ = False

    def append(self, __object: _T) -> None:
        with self.__cond__:
            self.append(__object)
            self.__cond__.notify_all()

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
            self.__cond__.notify_all()

    @synchronized
    def sub(self):
        """Subscribe a thread by returning condition variable to list updates"""
        return self.__cond__
