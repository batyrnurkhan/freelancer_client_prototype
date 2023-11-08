# views.py

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.urls import reverse_lazy
from .models import Order
from .forms import OrderForm

class OrderListView(LoginRequiredMixin, generic.ListView):
    model = Order
    template_name = 'core/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(client=self.request.user)

class OrderCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'core/order_form.html'
    success_url = reverse_lazy('listings:orders_list')  # Adjust to your order list view's name

    def form_valid(self, form):
        form.instance.client = self.request.user
        return super().form_valid(form)

    def test_func(self):
        # Ensure only clients can create orders
        return self.request.user.user_type == 'client'


from django.views.generic import DetailView
from .models import Order

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'core/order_detail.html'
    context_object_name = 'order'
    slug_url_kwarg = 'slug'


# listings/views.py

# from .models import Job
# from .forms import JobForm
# from django.shortcuts import render
# from django.views.generic import ListView, CreateView, UpdateView, DetailView
#
#
# class JobListView(LoginRequiredMixin, ListView):
#     model = Job
#     template_name = 'core/job_list.html'
#
#     def get_queryset(self):
#         if self.request.user.user_type == 'freelancer':
#             return Job.objects.filter(freelancer=self.request.user)
#         else:
#             return Job.objects.filter(client=self.request.user)
#
# class JobCreateView(LoginRequiredMixin, CreateView):
#     model = Job
#     form_class = JobForm
#     template_name = 'core/job_form.html'
#     success_url = reverse_lazy('job_list')
#
#     def form_valid(self, form):
#         # Assign the client based on the current user
#         form.instance.client = self.request.user
#         return super().form_valid(form)
#
# class JobDetailView(LoginRequiredMixin, DetailView):
#     model = Job
#     template_name = 'core/job_detail.html'
#
# class JobUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
#     model = Job
#     form_class = JobForm
#     template_name = 'core/job_form.html'
#     success_url = reverse_lazy('job_list')
#
#     def test_func(self):
#         job = self.get_object()
#         return self.request.user == job.client or self.request.user == job.freelancer