from django import forms

from .models import *


class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homeworks
        fields = ['Heading', 'StartTime', 'EndTime', 'Description', "AttachmentUrl"]
        widgets = {
            forms.TextInput(attrs={'class': 'form-control'})
        }
