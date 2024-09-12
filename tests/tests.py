import unittest
import sensorTest
import streamProcessorTest
import statisticTest
import utilitiesTest

class TestSum(unittest.TestCase):
    def testEquals(self):
        """
        Test summing a list of integers
        """
        data = [3, 4, 2]
        result = sum(data)
        self.assertEqual(result, 9)

    def test_bad_type(self):
        data = "not a number"
        with self.assertRaises(TypeError):
            result = sum(data)


if __name__ == '__main__':
    # run all tests with verbosity
    suite = unittest.TestLoader().loadTestsFromModule(streamProcessorTest)
    unittest.TextTestRunner(verbosity=2).run(suite)

    suite = unittest.TestLoader().loadTestsFromModule(statisticTest)
    unittest.TextTestRunner(verbosity=2).run(suite)

    suite = unittest.TestLoader().loadTestsFromModule(utilitiesTest)
    unittest.TextTestRunner(verbosity=2).run(suite)

    suite = unittest.TestLoader().loadTestsFromModule(sensorTest)
    unittest.TextTestRunner(verbosity=2).run(suite)