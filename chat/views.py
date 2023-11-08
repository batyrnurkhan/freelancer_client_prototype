from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Chat, Message
from .forms import MessageForm
from accounts.models import CustomUser

class ChatListView(LoginRequiredMixin, View):
    def get(self, request):
        chats = request.user.chats.all()
        return render(request, 'core/chat_list.html', {'chats': chats})

class ChatDetailView(LoginRequiredMixin, View):
    def get(self, request, chat_id):
        chat = get_object_or_404(Chat, id=chat_id)
        # Ensure the user is a participant in the chat
        if request.user not in chat.participants.all():
            return redirect('chat_list')
        messages = chat.messages.all()
        return render(request, 'core/chat_detail.html', {'chat': chat, 'messages': messages})

    def post(self, request, chat_id):
        chat = get_object_or_404(Chat, id=chat_id)
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.chat = chat
            message.save()
        return redirect('core/chat_detail.html', chat_id=chat_id)

class ChatCreateView(LoginRequiredMixin, View):
    def get(self, request, username):
        client = get_object_or_404(CustomUser, username=username)
        if request.user.user_type == 'freelancer' and client.user_type == 'client':
            chat, created = Chat.objects.get_or_create()
            chat.participants.add(request.user, client)
            return redirect('core/chat_detail', chat_id=chat.pk)
        else:
            return redirect('chat_list')
# ... other necessary views
class SendMessageView(LoginRequiredMixin, View):
    def post(self, request, chat_id):
        chat = get_object_or_404(Chat, pk=chat_id)
        form = MessageForm(request.POST)

        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.chat = chat
            message.save()
            return redirect('chat_detail', chat_id=chat_id)
        else:
            # Handle the case where the form is not valid
            return render(request, 'core/chat_detail.html', {'form': form, 'chat': chat})

from django.views.generic import ListView
from .models import CustomUser

class ClientListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'core/clients_list.html'

    def get_queryset(self):
        # Only show users with the 'client' role.
        return CustomUser.objects.filter(user_type='client')


from django.views import View
from django.shortcuts import redirect, get_object_or_404
from .models import Chat, CustomUser


def chat_detail(request, chat_id):
    chat = Chat.objects.get(pk=chat_id)
    messages = chat.messages.all()  # Make sure 'messages' is a related_name in your Message model
    return render(request, 'core/chat_detail.html', {'chat': chat, 'messages': messages})

class StartChatView(LoginRequiredMixin, View):
    def get(self, request, username):
        # Assume 'freelancer' is the context variable in freelancer_detail.html
        freelancer = get_object_or_404(CustomUser, username=username)


        # Here we check if there's an existing chat between the two users
        chat = Chat.objects.filter(participants__in=[request.user, freelancer]).distinct().first()

        if not chat:
            # If no chat exists, create a new one
            chat = Chat.objects.create()
            chat.participants.add(request.user, freelancer)
            chat.save()

        # Redirect to the chat detail view
        return redirect('chat:chat_detail', chat_id=chat.pk)