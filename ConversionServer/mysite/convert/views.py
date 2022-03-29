from django.http import HttpRequest, HttpResponse

from django.shortcuts import render
from .forms import sendableFile
import numpy

def convert(request):
    if request.method == "GET":
        form = sendableFile()
        return render(request, "convert.html", {"form": form})

    elif request.method == "POST":
        form = sendableFile(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data["file"]
            np = numpy.load(file)
            return HttpResponse(file.name + ": recieved succesfully\n" + numpy.array2string(np))

        return HttpResponse("failed")
        