from django.urls import reverse_lazy, reverse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from .models import Profile, FreelancerProfile, ClientProfile, Skill
from .forms import CustomUserCreationForm, ProfileForm, FreelancerProfileForm, ClientProfileForm
from django.db import transaction
from listings.models import Order
from django.db.models import Count, Q
from django.core.mail import send_mail
from django.conf import settings

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

from .forms import CustomUserForm
from django.shortcuts import get_object_or_404

class ProfileUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'core/edit_profile.html'
    form_class = CustomUserForm  # Assume this is the form for the CustomUser model
    success_url = reverse_lazy('accounts:profile_detail')
    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if not context.get('form'):
            context['form'] = self.form_class(instance=user)
        if user.user_type == 'freelancer':
            context['profile_form'] = FreelancerProfileForm(instance=user.freelancer_profile)
        elif user.user_type == 'client':
            context['profile_form'] = ClientProfileForm(instance=user.client_profile)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        user = self.request.user  # Define 'user' by getting it from the request

        if user.user_type == 'freelancer':
            profile_form = FreelancerProfileForm(request.POST, request.FILES, instance=user.freelancer_profile)
        elif user.user_type == 'client':
            profile_form = ClientProfileForm(request.POST, request.FILES, instance=user.client_profile)
        else:
            profile_form = None  # or handle as appropriate for your application

        if form.is_valid() and profile_form and profile_form.is_valid():
            return self.form_valid(form, profile_form)
        else:
            return self.form_invalid(form, profile_form)

    def form_valid(self, user_form, profile_form):
        user_form.save()
        profile_form.save()
        messages.success(self.request, 'Profile updated successfully')
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, user_form, profile_form):
        return self.render_to_response(self.get_context_data(form=user_form, profile_form=profile_form))


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