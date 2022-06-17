import unittest


class TestSum(unittest.TestCase):
    def test_Statistics(self):
        """
        This test creates and object Statistics with mock data and checks if the data is well processed and
        the extracted json with all the calculations is correct
        """
        labels = [1, 2, 3, 2, 3]
        scores = [1, 0.5, 0.25, 0.4, 0]
        times = [10, 20, 30, 40, 25]
        boxes = []
        stest = Statistics({'ref_boxes': boxes, 'ref_scores': scores, 'ref_labels': labels, 'ref_time': times})
        stest.process()
        self.assertEqual(stest.totals, [1, 1, 0])

        self.assertEqual(stest.to_json(), {'Cars': 1, 'Persons': 1, 'Bicycles': 0, 'average_time': 25.0,
                                           'standard_deviation_time': 11.180339887498949})

    def test_Reference(self):
        """
        This test creates an object ReferenceStatistics with with information about a specific frame.
        It processes the data, checks if everything is alright and tries to extract the correct json from it,
        testing all calculation methods we have defined.

        Input 5 measures:
        1st: car with all ok
        2nd: person with low score
        3rd: bycicle with even lower score
        4th: bycicle but wrong label
        5th: car with box not matching reference
        """
        labels = [1, 2, 3, 1, 1]
        scores = [1, 0.5, 0.25, 1, 1]
        times = [10, 20, 30, 20, 15]
        boxes = [[10, 10, 10, 10, 10, 10], [20, 20, 20, 20, 20, 20], [30, 30, 30, 15, 15, 45], [40, 40, 40, 40, 40, 40],
                 [50, 50, 50, 30, 30, 30]]
        reference = [[[10, 10, 10, 10, 10, 10, 1], [20, 20, 20, 20, 20, 20, 2], [30, 30, 30, 15, 15, 45, 3],
                      [40, 40, 40, 40, 40, 40, 3], [90, 90, 90, 30, 30, 30, 1]]]
        stest = ReferenceStatistics({'ref_boxes': boxes, 'ref_scores': scores, 'ref_labels': labels, 'ref_time': times},
                                    "")
        stest.reference = reference
        stest.process()
        self.assertEqual(stest.totals, [3, 1, 0])
        self.assertEqual(stest.tp, [1, 1, 1])
        self.assertEqual(stest.fp, [0, 0, 1])
        self.assertEqual(stest.fn, [1, 0, 0])

        self.assertEqual(stest.to_json(), {'Cars': 3, 'Persons': 1, 'Bicycles': 0, 'average_time': 19.0,
                                           'standard_deviation_time': 7.416198487095663,
                                           'precision': {'Cars': 1.0, 'Persons': 1.0, 'Bicycles': 0.5,
                                                         'macro_avg': 0.8333333333333334, 'weighted_avg': 1.0},
                                           'recall': {'Cars': 0.5, 'Persons': 1.0, 'Bicycles': 1.0,
                                                      'macro_avg': 0.8333333333333334, 'weighted_avg': 0.625},
                                           'f_score': {'Cars': 0.6666666666666666, 'Persons': 1.0,
                                                       'Bicycles': 0.6666666666666666, 'macro_avg': 0.7777777777777777,
                                                       'weighted_avg': 0.75}})


if __name__ == '__main__':
    unittest.main()