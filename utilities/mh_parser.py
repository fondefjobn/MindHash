from abstract_parser import ParserInput, ParserOutput

"""
@Module: PCDet to MindHash JSON parser
@Description: Parses PCDet evaluation tool predictions output to MindHash JSON output template
@Author: Lubor Budaj
"""
threshold = 0.7     #TODO: should be defined elsewhere

class SAParser(ParserInput, ParserOutput):
    """
    Parser for MindHash client StreetAnalytics work specific output
    """

    def initialize(self, data):
        self.boxes = data['ref_boxes']
        self.scores = data['ref_scores']
        self.labels = data['ref_labels']

    def to_json(self):
        output = []
        for box, label, score in zip(self.boxes, self.labels, self.scores):
            if score > threshold:
                output.append({
                    "measurement": "tracked_object",
                    "tags": {
                        "object_id": -1,
                        "object_type": label,
                    },
                    "time": -1,  # From recording start time + frame * 1 / framerate
                    "fields": {
                        "object_id": -1,
                        "object_type": label,
                        "length": box[3],
                        "width": box[4],
                        "height": box[5],
                        "x": box[0],  # from centroid x
                        "y": box[1],  # from centroid y
                        "velocity": -1,
                        "ma_velocity": -1,
                    }
                })
        return output
