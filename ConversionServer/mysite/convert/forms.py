from django import forms


class sendableFile(forms.Form):
    file = forms.FileField()
