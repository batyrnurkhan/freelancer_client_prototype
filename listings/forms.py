# forms.py

from django import forms
from .models import Order, Job
from accounts.models import Skill

from django import forms
from .models import Order
from accounts.models import Skill

class OrderForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        help_text='Select the skills required for this order.'
    )

    class Meta:
        model = Order
        fields = ['title', 'description', 'skills', 'price']

    # If you need any custom validation, you can add it here
    # For example:
    def clean_skills(self):
        skills = self.cleaned_data.get('skills')
        # Perform your validation here
        return skills


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