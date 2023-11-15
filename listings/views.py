from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, View
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Order
from .forms import OrderForm
from accounts.models import Skill

# List view for all orders, with separation of open and taken orders for freelancers
class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'core/orders/order_list.html'
    context_object_name = 'orders'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['open_orders'] = self.model.objects.filter(status='open')
        if self.request.user.is_authenticated and self.request.user.user_type == 'freelancer':
            context['taken_orders'] = self.model.objects.filter(
                freelancer=self.request.user.freelancer_profile,
                status='in_progress'
            )
        return context


# View for creating a new order, restricted to clients
class OrderCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'core/orders/order_form.html'
    success_url = reverse_lazy('listings:orders_list')

    def form_valid(self, form):
        form.instance.client = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.user_type == 'client'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skills'] = Skill.objects.all()
        return context


# Detailed view of a specific order
class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'core/orders/order_detail.html'
    context_object_name = 'order'
    slug_url_kwarg = 'slug'


# View for updating an existing order, restricted to the client who created it or admins
class OrderUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'core/orders/order_form.html'
    context_object_name = 'order'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('listings:orders_list')

    def form_valid(self, form):
        return super().form_valid(form)

    def test_func(self):
        order = self.get_object()
        return self.request.user == order.client or self.request.user.is_staff


# View for freelancers to take an order
class TakeOrderView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        if order.status == 'open':
            order.freelancer = request.user.freelancer_profile
            order.status = 'in_progress'
            order.save()
            messages.success(request, 'You have successfully taken the order.')
            return redirect('listings:orders_list')
        messages.error(request, 'This order is no longer available.')
        return redirect('listings:orders_list')


# View for updating the status of an order
class UpdateOrderStatusView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        new_status = request.POST.get('status')
        if new_status in [choice[0] for choice in Order.STATUS_CHOICES]:
            order.status = new_status
            order.save()
            messages.success(request, 'Order status has been updated.')
            return redirect('listings:order_detail', slug=order.slug)
        messages.error(request, 'Invalid order status.')
        return redirect('listings:order_detail', slug=order.slug)

    def test_func(self):
        order = self.get_object()
        return self.request.user == order.client.user


# View for freelancers to see their taken orders
class TakenOrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'core/orders/taken_orders_list.html'
    context_object_name = 'taken_orders'

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.user_type == 'freelancer':
            return self.model.objects.filter(
                freelancer=self.request.user.freelancer_profile,
                status='in_progress'
            )
        return self.model.objects.none()
