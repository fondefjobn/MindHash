class parser():
    def __init__(self, output):
        self.boxes = output['ref_boxes']
        self.scores = output['ref_scores']
        self.labels = output['ref_labels']

    def to_json(self):
        output = []
        for box, label in zip(self.boxes, self.labels):
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
                                "height":box[5],
                                "x": box[0],  # from centroid x
                                "y": box[1],  # from centroid y
                                "velocity": -1,
                                "ma_velocity": -1,
                            }
            })
        return output