from django.forms import inlineformset_factory
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from .models import Profile, FreelancerProfile, ClientProfile, Skill, CustomUser
from .forms import CustomUserCreationForm, ProfileForm, FreelancerProfileForm, ClientProfileForm
from django.db import transaction
from listings.models import Order
from django.db.models import Count, Q
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import UpdateView
from django.views.generic import UpdateView

class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('accounts:signin')  # Adjust to your sign-in view's name
    template_name = 'core/signup.html'

    def form_valid(self, form):
        with transaction.atomic():  # Use atomic to avoid partial commits
            user = form.save()  # Save the user first, to get a user id.

            # Check if the profiles already exist to prevent IntegrityError
            if user.user_type == 'freelancer' and not hasattr(user, 'freelancer_profile'):
                FreelancerProfile.objects.create(user=user)
            elif user.user_type == 'client' and not hasattr(user, 'client_profile'):
                ClientProfile.objects.create(user=user)
            else:
                # Handle other cases or raise an error
                print("User type is not set or profile already exists for the user: {}".format(user.email))

            # Send activation email
            self.send_activation_email(user)

        return super(SignUpView, self).form_valid(form)

    def send_activation_email(self, user):
        token = user.activation_token
        activation_link = f"{self.request.build_absolute_uri('/')[:-1]}{reverse_lazy('accounts:activate', args=[token])}"
        subject = "Activate your account"
        message = f"Hi {user.username}, Please click the following link to activate your account: {activation_link}"
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])


class SignInView(LoginView):
    template_name = 'core/signin.html'


from django.views.generic import DetailView

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'core/profile_detail.html'
    context_object_name = 'user'

    def get_object(self):
        # Ensures the user object is returned for the detail view
        return get_object_or_404(CustomUser, username=self.request.user.username)

    def get_context_data(self, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        user = self.request.user

        # Check if the user is a client and add closed orders to context
        if user.user_type == 'client':
            closed_orders = Order.objects.filter(client=user, status='closed')
            context['closed_orders'] = closed_orders
        return context


from django.views.generic import ListView
from .models import CustomUser
from django.db.models import Q

class FreelancerListView(ListView):
    model = CustomUser
    template_name = 'core/freelancer_list.html'
    context_object_name = 'freelancers'

    def get_queryset(self):
        queryset = CustomUser.objects.get_freelancers()
        search_query = self.request.GET.get('search', '')
        skill_filter = self.request.GET.getlist('skills')  # 'skills' is the name of the input

        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(freelancer_profile__skill_desc__icontains=search_query)
            )

        if skill_filter:
            queryset = queryset.filter(
                freelancer_profile__skills__id__in=skill_filter
            ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super(FreelancerListView, self).get_context_data(**kwargs)
        context['selected_skills'] = self.request.GET.getlist('skills')  # 'skills' should match your form's input name
        context['skills'] = Skill.objects.all()
        return context

class FreelancerDetailView(LoginRequiredMixin, generic.DetailView):
    model = FreelancerProfile
    template_name = 'core/freelancer_detail.html'
    context_object_name = 'freelancer'

    def get_object(self):
        return get_object_or_404(FreelancerProfile, pk=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        freelancer = self.get_object()
        context['orders_in_request'] = Order.objects.filter(freelancer=freelancer, status='in_request')
        return context

class ClientListView(LoginRequiredMixin, ListView):
    model = CustomUser  # Update this if you have a specific Client model
    template_name = 'core/not usage pages/clients_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        return CustomUser.objects.filter(user_type='client')

class ClientDetailView(LoginRequiredMixin, generic.DetailView):
    model = ClientProfile  # Update this if you have a specific Client model
    template_name = 'core/not usage pages/client_detail.html'
    context_object_name = 'client'

    def get_object(self):
        return get_object_or_404(ClientProfile, pk=self.kwargs.get('pk'))

from django.views.generic.edit import CreateView
from .models import Rating, FreelancerProfile

class RatingCreateView(LoginRequiredMixin, CreateView):
    model = Rating
    fields = ['score', 'review']
    template_name = 'core/rating_form.html'

    def form_valid(self, form):
        form.instance.order = Order.objects.get(id=self.kwargs['order_id'])
        form.instance.freelancer = FreelancerProfile.objects.get(id=self.kwargs['freelancer_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('order_detail', kwargs={'slug': self.object.order.slug})

from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy

class LogoutView(LogoutView):
    """
    Custom logout view that can handle additional logout logic.
    """

    # You can specify a 'next_page' attribute to redirect after logout
    next_page = reverse_lazy('home')  # Adjust to where you'd like to redirect after logout

    def dispatch(self, request, *args, **kwargs):
        # Here you can add any additional logic you want to perform during logout
        # For example, you can add a message to the user
        return super().dispatch(request, *args, **kwargs)


from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
def activate_account(request, token):
    try:
        user = CustomUser.objects.get(activation_token=token)
        if user.email_verified:
            messages.info(request, "Your account is already activated. Please log in.")
        else:
            user.email_verified = True
            user.activation_token = ''
            user.save()
            messages.success(request, "Your account has been activated. Please log in.")
        return redirect('accounts:signin')  # Replace 'accounts:signin' with the name of your login URL
    except CustomUser.DoesNotExist:
        messages.error(request, "Activation link is invalid!")
        return redirect('accounts:signin')  # Same here


from django.shortcuts import render
from django.db import models
from .forms import SearchForm
from .models import FreelancerProfile

from django.db.models import Q
from .models import FreelancerProfile, Skill

def search_freelancers(request):
    query = request.GET.get('search', '')
    if query:
        skills = Skill.objects.filter(name__icontains=query)
        freelancers = FreelancerProfile.objects.filter(
            Q(skills__in=skills) |
            Q(user__username__icontains=query) |
            Q(skill_desc__icontains=query) |
            Q(portfolio__icontains=query) |
            Q(reviews__icontains=query)
        ).distinct()
    else:
        freelancers = FreelancerProfile.objects.none()  # Or all() if you prefer to show all by default

    return render(request, 'core/freelancer_search_results.html', {
        'freelancers': freelancers,
        'query': query
    })


from django.http import JsonResponse
from .models import Skill

def skill_search(request):
    search_text = request.GET.get('search_text', '')
    skills = Skill.objects.filter(name__icontains=search_text).values('name')
    return JsonResponse({'skills': list(skills)})

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'core/orders/order_list.html'  # Update this to your actual template name
    context_object_name = 'orders'

    def get_queryset(self):
        queryset = super().get_queryset()
        selected_skills = self.request.GET.getlist('selected_skills')

        if selected_skills:
            queryset = queryset.filter(skills__name__in=selected_skills).distinct()

        # You can add additional filtering here if needed

        return queryset

from django.contrib.auth.decorators import login_required

@login_required
def update_client_profile(request):
    try:
        profile = request.user.client_profile
    except ClientProfile.DoesNotExist:
        profile = ClientProfile(user=request.user)

    if request.method == 'POST':
        form = ClientProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile_detail')

    else:
        form = ClientProfileForm(instance=profile)

    context = {'form': form}
    return render(request, 'core/update_client_profile.html', context)

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from .models import FreelancerProfile, CustomUser
from .forms import FreelancerProfileForm, CustomUserForm
from django.contrib import messages

class FreelancerProfileUpdateView(LoginRequiredMixin, View):
    template_name = 'core/edit_profile.html'
    user_form_class = CustomUserForm
    profile_form_class = FreelancerProfileForm
    success_url = reverse_lazy('accounts:profile_detail')  # Adjust as necessary

    def get(self, request, *args, **kwargs):
        user = request.user
        user_form = self.user_form_class(instance=user)
        profile, created = FreelancerProfile.objects.get_or_create(user=user)
        profile_form = self.profile_form_class(instance=profile)
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form
        })

    def post(self, request, *args, **kwargs):
        user = request.user
        user_form = self.user_form_class(request.POST, instance=user)
        profile, created = FreelancerProfile.objects.get_or_create(user=user)
        profile_form = self.profile_form_class(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect(self.success_url)
        else:
            messages.error(request, "There was an error updating your profile.")
            return render(request, self.template_name, {
                'user_form': user_form,
                'profile_form': profile_form
            })

import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def create_user_in_drf_project(sender, instance, created, **kwargs):
    if created:
        data = {
            "username": instance.username,
            "email": instance.email,
            "password": instance.password,  # Handle this securely
            "role": instance.user_type,  # Ensure user_type from Django maps to role in DRF
            "first_name": instance.first_name,
            "last_name": instance.last_name
        }
        try:
            response = requests.post(settings.DRF_PROJECT_API_URL, json=data)
            if response.status_code != 201:
                print("Failed to create user in DRF project. Status Code:", response.status_code)
                print("Response:", response.json())  # This will print the response body from the DRF project
        except requests.exceptions.RequestException as e:
            print("API call failed:", e)

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer
class UserRegistrationAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)