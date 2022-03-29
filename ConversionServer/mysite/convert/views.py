from IPython.utils import io
from django.http import HttpResponse
import numpy as np


def convert(request):
    data = np.load(io.BytesIO(request.content))      #input
        
    return HttpResponse(data, content_type='application/json')
