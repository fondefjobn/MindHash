import unittest
from tools.structs import PopList, CachedList
import numpy as np
from threading import Thread, Event
from time import sleep


class TestPopList(unittest.TestCase):

    def test_constructor(self):
        pop_list1 = PopList()
        self.assertEqual(len(pop_list1), 0)

        dict2 = {
            1: '1',
            2: '2'
        }
        pop_list2 = PopList(dict2)
        self.assertEqual(len(pop_list2), len(dict2))
        for i in dict2:
            self.assertEqual(pop_list2[i], dict2[i])

    def test_query(self):
        data = ["1", "2", "3"]

        pop_list = PopList()

        def thread_1():
            sleep(1)
            event = Event()
            pop_list.append(data[0])
            pop_list.append(data[1])
            self.assertEqual(pop_list.qy(2, event), data[2])

        def thread_2():
            event = Event()
            self.assertEqual(pop_list.qy(0, event), data[0])
            self.assertEqual(pop_list.qy(1, event), data[1])
            pop_list.append(data[2])

        t1 = Thread(target=thread_1)
        t2 = Thread(target=thread_2)

        t1.start()
        t2.start()

    def test_clean(self):
        data = ['1', '2', '3']

        pop_list = PopList()
        for i in data:
            pop_list.append(i)
        pop_list.clean(0, 1)
        self.assertEqual(len(pop_list), len(data))

        self.assertEqual(pop_list.qy(2, Event()), data[2])


class TestCachedList(unittest.TestCase):

    def test_constructor(self):
        cached_list = CachedList()
        self.assertEqual(len(cached_list), 0)

    def test_memory_usage(self):
        num_arrays = 1000
        elements_per_array = 10**6

        cached_list = CachedList()
        for i in range(num_arrays):
            cached_list.append(np.arange(i, i + elements_per_array))

        self.assertEqual(len(cached_list), num_arrays)

        for i in range(num_arrays):
            self.assertTrue(np.array_equal(cached_list[i], np.arange(i, i + elements_per_array)))


if __name__ == '__main__':
    unittest.main()

