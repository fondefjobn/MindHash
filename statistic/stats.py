from typing import List, Tuple

from tools.pipes import RNode
from tools.structs import PopList

tn = 0                  # true negatives (constant 0)
threshold = 0.7         # TODO: assignment is already somewhere else - use that instead
object_names = ['Cars', 'Bicycles', 'Persons']

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

    def __init__(self, data, reference): #TODO basic class without reference, super class with reference
        self.boxes = data['ref_boxes']
        self.scores = data['ref_scores']
        self.labels = data['ref_labels']
        self.reference = reference             # reference 

        #TODO: split in 3 categories
        self.tp = 0                            # true positives
        self.fp = 0                            # false positives
        self.fn = 0                            # false negatives

        self.totals = [0] * len(object_names)  # count number of occurences for each object type

    def process(self):
        for score, label in zip(self.scores, self.labels):
            if score >= threshold:
                self.totals[label] += 1
        #TODO: reference

    def to_json(self):
        output = {}
        for obj, count in zip(object_names, self.totals):
            output[obj] = count
        output['precision'] = self.precision()
        output['recall'] = self.recall()
        output['f_score'] = self.f_score()
        return output

    def precision(self):
        return self.tp / (self.tp + self.fp)

    def recall(self):
        return self.tp / (self.tp + self.fn)

    def f_score(self):
        return 2 * self.precision() * self.recall() / (self.precision() + self.recall())
