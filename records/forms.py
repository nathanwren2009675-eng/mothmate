from django import forms
from .models import MothSighting


class MothSightingForm(forms.ModelForm):
    class Meta:
        model = MothSighting
        fields = '__all__'  # ✅ Auto-includes EVERY field from your model
        exclude = ['user']   # ✅ Except the user (we set it automatically)