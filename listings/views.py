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

    def get_queryset(self):
        # Exclude orders with 'closed' and 'in_progress' status
        queryset = super().get_queryset().exclude(status__in=['closed', 'in_progress'])

        skill_query_list = self.request.GET.getlist('skills')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')

        if skill_query_list:
            queryset = queryset.filter(skills__name__in=skill_query_list).distinct()
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_skills'] = self.request.GET.getlist('skills')
        context['all_skills'] = Skill.objects.all()
        return context


# View for creating a new order, restricted to clients
class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'core/orders/order_form.html'
    success_url = reverse_lazy('listings:orders_list')

    def form_valid(self, form):
        order = form.save(commit=False)
        order.client = self.request.user  # Adjust as necessary for your user model
        order.save()
        form.save_m2m()
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Form errors:", form.errors)  # Log form errors
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skills'] = Skill.objects.all()  # Pass skills to the context if needed for filtering or display
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

from django.db.models import Count
from chat.models import Chat, Message
# View for freelancers to take an order

class TakeOrderView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        if order.status == 'open':
            # Removed the line that assigns the freelancer to the order
            order.status = 'in_request'  # Optionally, keep or remove this line based on your requirements
            order.save()
            messages.success(request, 'Your interest in taking the order has been sent to the client.')

            # Proceed to send message to the client
            self.notify_client(order)

            return redirect('listings:orders_list')
        messages.error(request, 'This order is no longer available.')
        return redirect('listings:orders_list')

    def notify_client(self, order):
        client = order.client
        freelancer = self.request.user

        # Check if there's an existing chat between the client and the freelancer
        chat = Chat.objects.annotate(num_participants=Count('participants')).filter(
            num_participants=2, participants=client).filter(participants=freelancer).first()

        if not chat:
            # Create a new chat if it doesn't exist
            chat = Chat.objects.create()
            chat.participants.add(client, freelancer)

        # Create a message in the chat
        message_text = f"Hello, I have shown interest in your order titled '{order.title}'. Please review my profile and let me know if you're interested."
        Message.objects.create(author=freelancer, chat=chat, content=message_text)




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
    template_name = 'core/orders/taken_orders_list.html'  # Create this template
    context_object_name = 'taken_orders'

    def get_queryset(self):
        return Order.objects.filter(client=self.request.user, status='in_progress')

