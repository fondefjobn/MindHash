from typing import List, Tuple

from tools.pipes import RNode
from tools.structs import PopList
from statistics import stdev
from math import sqrt

tn = 0                    # true negatives (constant 0)
threshold = 0.7           # TODO: assignment is already somewhere else - use that instead
tolerance_margin = 0.15
object_names = ['Cars', 'Persons', 'Bycicles']

class Routines(RNode):
    """
    Statistic routine
    """

    @classmethod
    def script(cls, parser) -> bool:
        return False

    def __init__(self, state):
        super().__init__(state)

    def run(self, _input: List[PopList], output: PopList, **kwargs):
        pass

    def dependencies(self):
        from streamprocessor.stream_process import Routines as processor
        from OpenPCDet.tools.evaluate import Routines as detectors
        return [processor, detectors]


class Statistics:

    def __init__(self, data):
        self.boxes = data['ref_boxes']
        self.scores = data['ref_scores']
        self.labels = data['ref_labels']
        self.times = data['ref_time']

        self.totals = [0] * len(object_names)  # count number of occurences for each object type

    def process(self):
        for score, label in zip(self.scores, self.labels):
            if score >= threshold:
                self.totals[label] += 1

    def to_json(self):
        output = {}
        for obj, count in zip(object_names, self.totals):
            output[obj] = count
        output['average_time'] = self.average_detection_time
        output['standard_deviation_time'] = stdev(self.times)
        return output

    def average_detection_time(self):
        return sum(self.times) / len(self.times)

class Statistics_with_Reference(Statistics):

    def __init__(self, data, reference):
        Statistics.__init__(self, data)
        self.reference_boxes, self.reference_labels = reference  # ground truths (list of 8 element lists containg the bounding box and a label)

        # Split in 3 categories: 1-car, 2-pedestrian, 3-cyclist
        self.tp = [0] * len(object_names)  # true positives
        self.fp = [0] * len(object_names)  # false positives
        self.fn = [0] * len(object_names)  # false negatives

    def process(self):
        super().process()
        for label, ref_label, box, ref_box in zip(self.labels, self.ref_labels, self.boxes, self.ref_boxes):
            dist = self.distance_btw_points(box[0], box[7])
            ref_dist = self.distance_btw_points(ref_box[0], ref_box[7])
            dist_0 = self.distance_btw_points(box[0], ref_box[0])
            dist_7 = self.distance_btw_points(box[7], ref_box[7])
            margin = tolerance_margin * ref_dist
            if not (dist > ref_dist + margin or dist < ref_dist - margin
                or dist_0 > margin or dist_7 > margin):
                if label == ref_label:
                    self.tp[ref_label] += 1
                else:
                    self.fp[ref_label] += 1
            else:
                self.fn[label] += 1

    def sorting(self):
        for box, ref_box in zip(self.boxes, self.ref_boxes):
            box.sort(key = lambda x: (x[0], x[1], x[2]))
            ref_box.sort(key = lambda x: (x[0], x[1], x[2]))

    def distance_btw_points(self, box1, box2):
        sum = 0
        for x1, x2 in zip(box1, box2):
            sum += pow(x1 - x2, 2)
        return sqrt(sum)

    def to_json(self):
        output = super().to_json()
        output['precision'] = {}
        for i in range(len(object_names)):
            output['precision'][object_names[i]] = self.precision(i)
        output['precision']['macro_avg'] = self.macro_avg(self.precision)
        output['precision']['weighted_avg'] = self.weighted_avg(self.precision)
        output['recall'] = {}
        for i in range(len(object_names)):
            output['recall'][object_names[i]] = self.recall(i)
        output['recall']['macro_avg'] = self.macro_avg(self.recall)
        output['recall']['weighted_avg'] = self.weighted_avg(self.recall)
        output['f_score'] = {}
        for i in range(len(object_names)):
            output['f_score'][object_names[i]] = self.f_score(i)
        output['f_score']['macro_avg'] = self.macro_avg(self.f_score)
        output['f_score']['weighted_avg'] = self.weighted_avg(self.f_score)
        return output

    def precision(self, i):
        if self.tp[i] + self.fp[i] == 0: return 0
        return self.tp[i] / (self.tp[i] + self.fp[i])

    def recall(self, i):
        if self.tp[i] + self.fn[i] == 0: return 0
        return self.tp[i] / (self.tp[i] + self.fn[i])

    def f_score(self, i):
        if self.precision(i) + self.recall(i) == 0: return 0
        return 2 * self.precision(i) * self.recall(i) / (self.precision(i) + self.recall(i))

    def macro_avg(self, function):
        return sum(function(i) for i in range(len(object_names))) / len(object_names)

    def weighted_avg(self, function):
        if sum(self.totals) == 0: return 0
        return sum(function(i) * self.totals[i] for i in range(len(object_names))) / sum(self.totals)

    def accuracy(self):
        if sum(self.totals) == 0: return 0
        return sum(self.tp) / sum(self.totals)