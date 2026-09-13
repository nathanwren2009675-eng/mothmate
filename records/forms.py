from django import forms
from .models import MothSighting


class MothSightingForm(forms.ModelForm):
    class Meta:
        model = MothSighting
        fields = [
            'taxon', 'vernacular', 'site', 'gridref',
            'vice_county', 'quantity', 'stage', 'date',
            'recorder', 'determiner', 'method', 'comment'
        ]
        labels = {
            'taxon': 'Scientific Name',
            'vernacular': 'Common Name',
            'vice_county': 'Vice County',
        }