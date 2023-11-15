from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from .models import Profile, FreelancerProfile, ClientProfile, Skill
from .forms import CustomUserCreationForm, ProfileForm, FreelancerProfileForm, ClientProfileForm
from django.db import transaction
from listings.models import Order
from django.db.models import Count, Q


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

        return super(SignUpView, self).form_valid(form)


class SignInView(LoginView):
    template_name = 'core/signin.html'


from django.shortcuts import get_object_or_404
class ProfileUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'core/edit_profile.html'
    success_url = reverse_lazy('profile_detail')

    def get_form_class(self):
        if self.request.user.user_type == 'freelancer':
            return FreelancerProfileForm
        elif self.request.user.user_type == 'client':
            return ClientProfileForm
        else:
            return ProfileForm

    def get_object(self):
        if self.request.user.user_type == 'freelancer':
            return get_object_or_404(FreelancerProfile, user=self.request.user)
        elif self.request.user.user_type == 'client':
            return get_object_or_404(ClientProfile, user=self.request.user)
        else:
            # Assuming every user has a basic profile
            return get_object_or_404(Profile, user=self.request.user)

    def get_success_url(self):
        # You can customize the success URL based on the user type if needed
        if self.request.user.user_type == 'freelancer':
            return reverse_lazy('accounts:profile_detail')
        elif self.request.user.user_type == 'client':
            return reverse_lazy('accounts:profile_detail')
        else:
            return super().get_success_url()

class ProfileDetailView(LoginRequiredMixin, generic.DetailView):
    model = Profile
    template_name = 'core/profile_detail.html'

    def get_object(self):
        # Ensures that the Profile exists, or creates one if it doesn't
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def get_success_url(self):
        return reverse_lazy('accounts:edit_profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add client's orders to context if user is a client
        if self.request.user.user_type == 'client':
            context['client_orders'] = Order.objects.filter(client=self.request.user).order_by('-created_at')

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
        skill_filter = self.request.GET.getlist('skill')  # Get the list of selected skills
        search_query = self.request.GET.get('search')

        # Filter freelancers by search query
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        # Filter freelancers who have all the selected skills
        for skill_name in skill_filter:
            queryset = queryset.filter(freelancer_profile__skills__name=skill_name)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skills'] = Skill.objects.all()
        context['selected_skills'] = self.request.GET.getlist('skill')  # Pass the selected skills to the context
        return context

class FreelancerDetailView(LoginRequiredMixin, generic.DetailView):
    model = FreelancerProfile
    template_name = 'core/freelancer_detail.html'
    context_object_name = 'freelancer'

    def get_object(self):
        return get_object_or_404(FreelancerProfile, pk=self.kwargs.get('pk'))

class ClientListView(LoginRequiredMixin, ListView):
    model = CustomUser  # Update this if you have a specific Client model
    template_name = 'core/clients_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        return CustomUser.objects.filter(user_type='client')

class ClientDetailView(LoginRequiredMixin, generic.DetailView):
    model = ClientProfile  # Update this if you have a specific Client model
    template_name = 'core/client_detail.html'
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