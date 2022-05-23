import unittest


class TestSum(unittest.TestCase):
    def test_foo(self):
        """
        test explanation
        """
        self.assertEqual("foo", "foo")

    def test_bar(self):
        """
        test explanation
        """
        data = "not a number"
        with self.assertRaises(TypeError):
            result = sum(data)


if __name__ == '__main__':
    unittest.main()
