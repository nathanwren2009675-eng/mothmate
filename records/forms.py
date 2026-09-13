from django import forms
from .models import MothSighting

class MothSightingForm(forms.ModelForm):
    class Meta:
        model = MothSighting
        fields = '__all__'
        exclude = ['user']