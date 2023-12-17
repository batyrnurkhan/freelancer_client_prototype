from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Profile

class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'user_type', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        # You can add any custom logic for first_name and last_name here if necessary
        if commit:
            user.save()
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_image', 'bio', 'location', 'birth_date']

from .models import FreelancerProfile, Skill

class FreelancerProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(), 
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = FreelancerProfile
        fields = ['first_name', 'last_name', 'skills', 'skill_desc', 'portfolio', 'profile_image', 'video']  # Include 'skill_desc' here

from .models import Rating

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score', 'review']

from .models import ClientProfile

class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = [
            'company_name',
            'company_website',
            'profile_image',
            'contact_name',
            'contact_email',
            'contact_phone',
            'company_description',
            'industry',
            'preferred_communication',
            'additional_notes'
        ]

    def __init__(self, *args, **kwargs):
        super(ClientProfileForm, self).__init__(*args, **kwargs)


from django import forms

class SearchForm(forms.Form):
    query = forms.CharField(label='Search for freelancers')
