from abstract_parser import ParserInput, ParserOutput
from OpenPCDet.tools.evaluate import labels

"""
@Module: Parser
@Description: Parser from PCDet evaluation tool predictions output to MindHash JSON output template
@Author: Lubor Budaj
"""

"""
Parser for MindHash client StreetAnalytics work specific output
"""
class SAParser(ParserInput, ParserOutput):
    
    """
    Initializes the parameters from 'data' dictionary, which is the output of PCDet
    """
    def initialize(self, data):
        self.boxes = data['ref_boxes']
        self.scores = data['ref_scores']
        self.labels = data['ref_labels']

    """
    Outputs a list of fictionaries. Each dictionary contains information
    about one detected object. Each dictionary is in format requested
    by Mindhash. The data that our evaluation tool does not provide are
    indetifies as -1.
    Note: time variable here is a time from beginning of the recording
    that we don't know during the evaluation, not an evaluation time.
    """
    def to_json(self):
        output = []
        for box, label in zip(self.boxes, self.labels):
            output.append({
                "measurement": "tracked_object",
                "tags": {
                    "object_id": label,
                    "object_type": labels[label],
                },
                "time": -1,
                "fields": {
                    "object_id": label,
                    "object_type": labels[label],
                    "length": box[3],
                    "width": box[4],
                    "height": box[5],
                    "x": box[0],
                    "y": box[1],
                    "velocity": -1,
                    "ma_velocity": -1,
                }
            })
        return output
