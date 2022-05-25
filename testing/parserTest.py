import unittest
from utilities.mh_parser import SAParser

"""
@Author Frank van Houten
"""
NUM_ITEMS_TEST = 2
BOX_1 = [20, 19, 18, 10, 9, 8, 0.2]
BOX_2 = [60, 59, 58, 15, 14, 13, 0.5]
REF_1 = 60
REF_2 = 70
LABEL_1 = 1
LABEL_2 = 2
REF_LABELS = [LABEL_1, LABEL_2]
REF_SCORES = [REF_1, REF_2]
REF_BOXES = [BOX_1, BOX_2]
test_output = {
    # ref_boxes : [x_center, y_center, z_center , length, width, height, rotate_z_axis_angle]
    "ref_boxes": REF_BOXES,
    # ref_scores : [normalized score percentage]
    "ref_scores": REF_SCORES,
    # ref_labels : [obj_label]
    "ref_labels": REF_LABELS
}


class TestParser(unittest.TestCase):

    def test_to_json(self):
        """
            Testing if the to_json function in the parser copies the values supplied to the class correctly to the new
            format.
            For keys that are not filled in using values from the supplied arguments we are just testing if they are not
            None.
        """

        json = SAParser(output=test_output).to_json()
        for i in range(NUM_ITEMS_TEST):
            # Test if labels are correctly ordered and copied
            self.assertEqual(json[i]['tags']['object_type'], REF_LABELS[i])
            self.assertEqual(json[i]['fields']['object_type'], REF_LABELS[i])
            # Test if the length is copied
            self.assertEqual(json[i]['fields']['length'], REF_BOXES[i][3])
            # Test if the width is copied
            self.assertEqual(json[i]['fields']['width'], REF_BOXES[i][4])
            # Test if the height is copied
            self.assertEqual(json[i]['fields']['height'], REF_BOXES[i][5])
            # Test if the x is copied
            self.assertEqual(json[i]['fields']['x'], REF_BOXES[i][0])
            # Test if the y is copied
            self.assertEqual(json[i]['fields']['y'], REF_BOXES[i][1])
            # Test if the rest of the arguments are not NULL
            self.assertIsNotNone(json[i]['tags']['object_id'])
            self.assertIsNotNone(json[i]['time'])
            self.assertIsNotNone(json[i]['fields']['object_id'])
            self.assertIsNotNone(json[i]['fields']['velocity'])
            self.assertIsNotNone(json[i]['fields']['ma_velocity'])


if __name__ == '__main__':
    unittest.main()
