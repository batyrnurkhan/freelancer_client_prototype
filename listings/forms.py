# forms.py

from django import forms
from .models import Order, Job
from accounts.models import Skill, FreelancerProfile
from django import forms
from .models import Order
from accounts.models import Skill

class OrderForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        help_text='Select the skills required for this order.'
    )

    # Add a ModelChoiceField for selecting a freelancer
    freelancer = forms.ModelChoiceField(
        queryset=FreelancerProfile.objects.all(),
        required=False,
        help_text='Select a freelancer for this order.'
    )

    class Meta:
        model = Order
        fields = ['title', 'description', 'skills', 'price', 'freelancer']  # Include the 'freelancer' field


class SkillSearchForm(forms.Form):
    skill_query = forms.CharField(required=False, label='Search Orders by Skills')

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