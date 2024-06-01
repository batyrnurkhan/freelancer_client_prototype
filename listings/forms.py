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
    freelancer = forms.CharField(
        required=False,
        help_text='Start typing to search for freelancers.',
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )

    class Meta:
        model = Order
        fields = ['title', 'description', 'skills', 'price', 'freelancer']

    def clean_freelancer(self):
        username = self.cleaned_data['freelancer']
        try:
            freelancer = FreelancerProfile.objects.get(user__username=username)
            return freelancer
        except FreelancerProfile.DoesNotExist:
            raise forms.ValidationError("Freelancer not found")


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

class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']  # Only include the status field

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.status == 'open':
            instance.freelancer = None
        if commit:
            instance.save()
        return instance


from accounts.models import Rating
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score', 'review']