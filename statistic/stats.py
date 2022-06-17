from typing import List, Tuple

from tools.pipeline import RNode
from tools.structs import PopList

from statistics import stdev
from bisect import bisect_left, bisect_right


class Routines(RNode):
    """
    Statistic routine
    """
    ix: int = 0

    def get_index(self) -> int:
        return self.ix

    @classmethod
    def script(cls, parser):
        parser.add_argument('--stats', help='Generate statistic')

    def __init__(self, state):
        super().__init__(state)

    @RNode.assist
    def run(self, _input: List[PopList], output: PopList, **kwargs):
        pass

    def dependencies(self):
        from streamprocessor.stream_process import Routines as processor
        from OpenPCDet.tools.detection import Routines as detectors
        return [processor, detectors]


class Statistics:

    threshold = 0.7    # TODO: assignment is already somewhere else - use that instead
    object_names = ['Cars', 'Persons', 'Bicycles']

    def __init__(self, data):

        self.boxes = data['ref_boxes']
        self.scores = data['ref_scores']
        self.labels = data['ref_labels']
        self.times = data['ref_time']

        self.totals = [0] * len(self.object_names)  # the number of occurrences for each object type

    def process(self):
        for score, label in zip(self.scores, self.labels):
            if score >= self.threshold:
                self.totals[label] += 1

    def to_json(self):
        output = {}
        for obj, count in zip(self.object_names, self.totals):
            output[obj] = count
        output['average_time'] = self.average_detection_time
        output['standard_deviation_time'] = stdev(self.times)
        return output

    def average_detection_time(self):
        return sum(self.times) / len(self.times)


class ReferenceStatistics(Statistics):

    leeway = 0.15      # margin percentage
    tn = 0             # true negatives (constant 0)

    def __init__(self, data, reference):
        super().__init__(data)
        self.reference = reference

        # Split in 3 categories: 1-car, 2-pedestrian, 3-cyclist
        self.tp = [0] * len(self.object_names)  # true positives
        self.fp = [0] * len(self.object_names)  # false positives
        self.fn = [0] * len(self.object_names)  # false negatives

    def find_and_compare_box(self, box, margin, left, right, label):
        for idx in range(left, right):
            cond = True
            for i in range(6):   # box dimensions definition
                if not (cond and self.reference[idx][i] + margin > box[i] >
                        self.reference[idx][i] - margin):
                    cond = False
            if cond:
                if label == self.reference[idx][6]:
                    self.tp[self.reference[idx][6]] += 1
                else:
                    self.fp[self.reference[idx][6]] += 1
                return

        self.fn[label] += 1

    def process(self):
        super().process()

        for label, box in zip(self.labels, self.boxes):
            margin = self.leeway * sum(box[3:6]) / 3
            box[0] -= margin
            left = bisect_left(self.reference, box)
            box[0] += 2 * margin
            right = bisect_right(self.reference, box)
            box[0] -= margin

            self.find_and_compare_box(box, margin, left, right, label)

    def sort_reference(self):
        self.reference.sort(key=lambda x: x[0])

    def to_json(self):
        output = {'count': {}}
        for obj, count in zip(self.object_names, self.totals):
            output['count'][obj] = count
        output['precision'] = {}
        for i in range(len(self.object_names)):
            output['precision'][self.object_names[i]] = self.precision(i)
        output['precision']['macro_avg'] = self.macro_avg(self.precision)
        output['precision']['weighted_avg'] = self.weighted_avg(self.precision)
        output['recall'] = {}
        for i in range(len(self.object_names)):
            output['recall'][self.object_names[i]] = self.recall(i)
        output['recall']['macro_avg'] = self.macro_avg(self.recall)
        output['recall']['weighted_avg'] = self.weighted_avg(self.recall)
        output['f_score'] = {}
        for i in range(len(self.object_names)):
            output['f_score'][self.object_names[i]] = self.f_score(i)
        output['f_score']['macro_avg'] = self.macro_avg(self.f_score)
        output['f_score']['weighted_avg'] = self.weighted_avg(self.f_score)
        return output

    def precision(self, i):
        return self.tp[i] / (self.tp[i] + self.fp[i])

    def recall(self, i):
        return self.tp[i] / (self.tp[i] + self.fn[i])

    def f_score(self, i):
        return 2 * self.precision(i) * self.recall(i) / (self.precision(i) + self.recall(i))

    def macro_avg(self, function):
        object_names = self.object_names
        return sum(function(i) for i in range(len(object_names))) / len(object_names)

    def weighted_avg(self, function):
        object_names = self.object_names
        return sum(function(i) * self.totals[i] for i in range(len(object_names))) / sum(self.totals)

    def accuracy(self):
        return sum(self.tp) / sum(self.totals)

