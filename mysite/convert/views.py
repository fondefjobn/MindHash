from IPython.utils import io
from django.http import HttpResponse
import numpy as np
import json


def convert(request):
    data = np.load(io.BytesIO(request.content))
    """
    Conversion goes here
    """
    dataJson = {}
    return HttpResponse(dataJson, content_type='application/json')
