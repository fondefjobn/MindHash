from IPython.utils import io
from django.http import HttpResponse
import numpy as np
import json


def convert(request):
    data = np.load(io.BytesIO(request.content))
    boxes = data['ref_boxes']
    scores = data['ref_scores']
    labels = data['ref_labels']

    json_output = []
    for box, label in zip(boxes, labels):
        json_output.append({
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
        
    return HttpResponse(json_output, content_type='application/json')