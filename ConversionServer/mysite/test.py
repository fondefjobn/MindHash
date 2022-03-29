import json
import numpy as np
from django.http import HttpResponse


def sampleConvert():
    url = 'http://127.0.0.1:8000/convert/'
    data = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])

    np.save('testData.npy',data)
    return HttpResponse(data, content_type='application/octet-stream')
    res = requests.get(url)