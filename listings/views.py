from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, View
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Order
from .forms import OrderForm, FeedbackForm
from accounts.models import Skill, Rating, FreelancerProfile


# List view for all orders, with separation of open and taken orders for freelancers
class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'core/orders/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        queryset = super().get_queryset().exclude(slug__isnull=True).exclude(slug__exact='')
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

from django.utils.text import slugify

# View for creating a new order, restricted to clients
class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'core/orders/order_form.html'
    success_url = reverse_lazy('listings:orders_list')

    def form_valid(self, form):
        order = form.save(commit=False)
        order.client = self.request.user  # Adjust as necessary for your user model
        order.slug = self.generate_unique_slug(order.title)
        order.save()
        form.save_m2m()
        return super().form_valid(form)

    def generate_unique_slug(self, title):
        base_slug = slugify(title)
        slug = base_slug
        num = 1
        while Order.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{num}"
            num += 1
        return slug

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

from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from .models import Order
from .forms import OrderUpdateForm
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from .models import Order
from .forms import OrderUpdateForm
from django.urls import reverse

class OrderDetailView2(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'core/orders/order_detail2.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = OrderUpdateForm(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = OrderUpdateForm(request.POST, instance=self.object)
        if form.is_valid():
            updated_order = form.save()
            messages.success(request, 'Order status updated successfully.')
            if updated_order.status == 'completed':
                # Redirect to feedback form
                return redirect('listings:feedback_form', order_id=updated_order.id)
            return redirect(self.get_success_url())
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('listings:order_detail2', kwargs={'slug': self.object.slug})

from django.views.generic.edit import FormView

class FeedbackView(LoginRequiredMixin, FormView):
    template_name = 'core/orders/feedback_form.html'
    form_class = FeedbackForm

    def form_valid(self, form):
        order = Order.objects.get(id=self.kwargs['order_id'])
        if order.freelancer:
            # Update or create the rating
            rating, created = Rating.objects.update_or_create(
                order=order,
                defaults={
                    'freelancer': order.freelancer,  # Ensure this is a direct reference to a FreelancerProfile instance
                    'score': form.cleaned_data['score'],
                    'review': form.cleaned_data['review']
                }
            )
            order.freelancer.update_ratings()  # Ensure this method doesn't improperly handle related sets
            return super().form_valid(form)
        else:
            # Properly handle cases where no freelancer is assigned
            messages.error(self.request, "No freelancer assigned to this order.")
            return self.form_invalid(form)

    def get_success_url(self):
        # Redirect to some success page or order detail page
        return reverse('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = Order.objects.get(id=self.kwargs['order_id'])
        return context


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

from django.http import JsonResponse
def search_freelancers(request):
    query = request.GET.get('query', '')
    freelancers = FreelancerProfile.objects.filter(user__username__icontains=query)
    return JsonResponse({
        'freelancers': [{'username': f.user.username} for f in freelancers]
    })


class ClientOrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'core/orders/client_orders_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        # Returns orders where the logged-in user is the client and have a non-empty slug
        return Order.objects.filter(client=self.request.user).exclude(slug__isnull=True).exclude(slug__exact='').order_by('-created_at')