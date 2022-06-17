from threading import Event
from typing import List, Optional, Union, Tuple, TypeVar, Set, Iterable, Dict, Any

from numpy.typing import NDArray
from wrapt import synchronized
import tempfile
import pickle

"""
@Module: Custom Data Structures
@Description: Contains classes extending functionalities (Decorators) or offering new functionalities from scratch.
Also contains data classes.
@Authors: Radu Rebeja, Bob van der Vuurst
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
    Lock is created within PopList
    For more details on Condition, Locks and Threads see:
    https://docs.python.org/3.8/library/threading.html#using-locks-conditions-and-semaphores-in-the-with-statement
    """
    _full_: bool
    _event_ls_: Set[Event]
    _ID_ = None
    _T = TypeVar("_T")
    _KT = TypeVar("_KT")
    _VT = TypeVar("_VT")
    _t_min_: int = 0
    _last_: _T

    def __init__(self, seq: Optional[Union[Iterable[Tuple], Dict]] = None, doc: str = ''):
        prev = {} if seq is None else seq
        super().__init__(prev)
        self._full_ = False
        self._event_ls_ = set()
        self._len_ = len(prev)
        self._last_ = self.get(self._len_, None)
        self.__doc__ += doc

    def append(self, __object: _T) -> None:
        """
          Appends an object to the PopList end
          and notifies all threads waiting in qy()
          Parameters
          ----------
          __object

          Returns
          -------

          """

        self[self.__len__()] = __object
        self._last_ = __object
        self._notify_all()

    def qy(self, ix: int, event: Event, timeout: float = None) -> _T:
        """
        Method to use for safe element querying.
        Conditionally-blocking method - method unblocks
        and returns an item only at the next update and availability of item
        or timeout.
        A timeout may return None.

        Parameters
        ----------
        ix : index to use for querying
        event : caller Event object to wait until query is available
        timeout : timeout for querying
        Returns
        -------

        """
        while ix not in self:
            self._event_ls_.add(event)
            event.wait(timeout=timeout)
            event.clear()
            self._event_ls_.remove(event)
            if ix not in self and self._full_:  # To avoid None checkers - pass last available frame
                return self._last_
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

    def clean(self, start: int = 0, end: int = None) -> None:
        """
        Method to clear elements from a PopList
        Parameters
        ----------
        start : index to start begin item removal
        end : index to stop item removal

        Returns
        -------

        """
        idxs: List[int]
        self._t_min_ = self.__len__() if ((end is None) or (end > self._len_)) else end
        idxs = list(range(start, self._t_min_))
        [self.pop(ix, None) for ix in idxs]

    def __setitem__(self, k: _KT, v: _VT) -> None:
        """

        """
        super().__setitem__(k, v)
        self._len_ = self.__len__() + 1

    @synchronized
    def __len__(self):
        """

        Returns
        -------
        int Elements added to the list,
        does not exclude cleared items from calculated length.
        """
        return self._len_

    def _notify_all(self):
        """
        Notify all waiting qy() callers of update.
        Returns
        -------

        """

        def notify(event: Event):
            event.set()

        list(map(notify, self._event_ls_.copy()))

    @property
    def first(self):
        """

        Returns
        -------
        int Index of first element
        """
        return self._t_min_


class MatrixCloud:
    """
    Our project standardization data-structure for point cloud data.
    All sensor outputs are converted to fit data into this class
    timestamp =  describing timestamp in UNIX epoch time
    xyz = numpy array XYZ coordinates
    channels = dict of numpy
    """

    def __init__(self):
        self.timestamps = None
        self.xyz: NDArray[(3, Any), float] = None
        self.channels = {
            Ch.NEAR_IR: None,
            Ch.SIGNAL: None,
            Ch.REFLECTIVITY: None
        }


class Ch:
    RANGE = 'RANGE'
    NEAR_IR = 'NEAR_IR'
    REFLECTIVITY = 'REFLECTIVITY'
    SIGNAL = 'SIGNAL'
    channel_arr = [RANGE, SIGNAL, NEAR_IR, REFLECTIVITY]  # exact order of fields


class CachedList:
    """
    A list where most of the data that isn't used is saved to temporary files.
    The CachedList will have the same functionality as a normal list,
    but it will not take as much memory.
    The list is seperated into blocks, where only the block where the last index was read
    and the end block of the list are stored into memory. The others are stored in files.
    """
    _BLOCK_SIZE = 50
    _cached_blocks: list
    _current_block: list
    _new_block: list

    def __init__(self):
        self._cached_blocks = []
        self._current_block = []
        self._new_block = []
        self.loaded_block = -1

    """
    Append an item to the list. If the block is full, save the block to a file.
    """
    def append(self, item):
        self._new_block.append(item)
        if len(self._new_block) >= self._BLOCK_SIZE:
            self._save_to_file()

    """
    Save the block to a temporary file and add the file to the file list. 
    """
    def _save_to_file(self):
        block = tempfile.NamedTemporaryFile()
        pickle.dump(self._new_block, block)
        block.flush()
        self._cached_blocks.append(block)
        self._new_block = []

    """
    Load block based on the index that is given, where the loaded block is located at
    _cached_blocks[item // BLOCK_SIZE]. 
    """
    def _load_from_file(self, item):
        block = item // self._BLOCK_SIZE
        with open(self._cached_blocks[block].name, 'rb') as file:
            self._current_block = pickle.load(file)
        self.loaded_block = block

    """
    Return the size of all the blocks stored in the files and the last block that has not been 
    saved to a file yet.
    """
    def __len__(self):
        return len(self._cached_blocks) * self._BLOCK_SIZE + len(self._new_block)

    """
    Get an item at the index for the list. There are three scenario's: 
    If the item is in the last block, then return the item from that last block
    If the item is in the currently loaded block, then return the item from the loaded block.
    Otherwise, the item is in a file and the file needs to be loaded first.
    """
    def __getitem__(self, item):
        if item >= len(self._cached_blocks) * self._BLOCK_SIZE:
            return self._new_block[item % self._BLOCK_SIZE]

        elif self.loaded_block * self._BLOCK_SIZE <= item < (self.loaded_block + 1) * self._BLOCK_SIZE:
            return self._current_block[item % self._BLOCK_SIZE]

        else:
            self._load_from_file(item)
            return self._current_block[item % self._BLOCK_SIZE]
