# forms.py

from django import forms
from .models import Order, Job

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['title', 'description', 'technology_stack', 'price']

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'due_date', 'status', 'deliverables']

    # Optionally, you can add custom validation, widgets, or help texts here.
    # For example:
    due_date = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date'}),
        help_text='Format: YYYY-MM-DD'
    )