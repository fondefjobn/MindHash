import unittest


class TestSum(unittest.TestCase):
    def test_Reference(self):
        """
        This test creates an object Statistics_with_Reference with specific values for totals, tps, fps and fns and
        tries to extract the correct json from it, testing all calculation methods we have defined.
        """
        stest = Statistics_with_Reference({}, {})
        stest.totals = [10, 20, 30]
        stest.tp = [3, 14, 16]
        stest.fp = [6, 4, 4]
        stest.fn = [1, 2, 10]

        self.assertEqual(stest.to_json(), {'count': {'Cars': 10, 'Persons': 20, 'Bycicles': 30},
                                           'precision': {'Cars': 0.3333333333333333, 'Persons': 0.7777777777777778,
                                                         'Bycicles': 0.8, 'macro_avg': 0.6370370370370371,
                                                         'weighted_avg': 0.7148148148148148},
                                           'recall': {'Cars': 0.75, 'Persons': 0.875, 'Bycicles': 0.6153846153846154,
                                                      'macro_avg': 0.7467948717948718,
                                                      'weighted_avg': 0.7243589743589745},
                                           'f_score': {'Cars': 0.46153846153846156, 'Persons': 0.823529411764706,
                                                       'Bycicles': 0.6956521739130435, 'macro_avg': 0.660240015738737,
                                                       'weighted_avg': 0.6992589678011674}})

    def test_bar(self):
        """
        test explanation
        """
        data = "not a number"
        with self.assertRaises(TypeError):
            result = sum(data)


if __name__ == '__main__':
    unittest.main()
