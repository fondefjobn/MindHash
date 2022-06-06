from typing import List, Tuple

from tools.pipes import RNode
from tools.structs import PopList

tn = 0                  # true negatives (constant 0)
threshold = 0.7         # TODO: assignment is already somewhere else - use that instead
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

    def __init__(self, data, reference):  # TODO basic class without reference, super class with reference
        self.boxes = data['ref_boxes']
        self.scores = data['ref_scores']
        self.labels = data['ref_labels']

        self.totals = [0] * len(object_names)  # count number of occurences for each object type

    def process(self):
        for score, label in zip(self.scores, self.labels):
            if score >= threshold:
                self.totals[label] += 1

    def to_json(self):
        output = {}
        for obj, count in zip(object_names, self.totals):
            output[obj] = count
        return output


class Statistics_with_Reference(Statistics):

    def __init__(self, data, reference):  # TODO basic class without reference, super class with reference
        self.reference = reference  # reference

        # Split in 3 categories: 1-car, 2-pedestrian, 3-cyclist
        self.tp = [0] * len(object_names)  # true positives
        self.fp = [0] * len(object_names)  # false positives
        self.fn = [0] * len(object_names)  # false negatives

    def process(self):
        for score, label in zip(self.scores, self.labels):
            if score >= threshold:
                self.totals[label] += 1
        # TODO: reference

    def to_json(self):
        output = {}
        output['count'] = {}
        for obj, count in zip(object_names, self.totals):
            output['count'][obj] = count
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
        return self.tp[i] / (self.tp[i] + self.fp[i])

    def recall(self, i):
        return self.tp[i] / (self.tp[i] + self.fn[i])

    def f_score(self, i):
        return 2 * self.precision(i) * self.recall(i) / (self.precision(i) + self.recall(i))

    def macro_avg(self, function):
        return sum(function(i) for i in range(len(object_names))) / len(object_names)

    def weighted_avg(self, function):
        return sum(function(i) * self.totals[i] for i in range(len(object_names))) / sum(self.totals)

    def accuracy(self):
        return sum(self.tp) / sum(self.totals)