from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Chat, Message
from .forms import MessageForm
from accounts.models import CustomUser
from django.db.models import Max

class ChatListView(LoginRequiredMixin, View):
    def get(self, request):
        # Annotate each chat with the timestamp of the latest message
        chats = request.user.chats.annotate(
            last_message_time=Max('messages__timestamp')
        ).order_by('-last_message_time')  # Order by this annotation in descending order

        # Preparing data for each chat
        chats_with_other_user = []
        for chat in chats:
            other_user = chat.participants.exclude(id=request.user.id).first()
            chats_with_other_user.append({
                'chat': chat,
                'other_user': other_user,
                'other_user_profile_image': self.get_profile_image_url(other_user),
            })

        return render(request, 'core/chat_list.html', {'chats_with_other_user': chats_with_other_user})

    def get_profile_image_url(self, user):
        if hasattr(user, 'freelancer_profile') and user.freelancer_profile.profile_image:
            return user.freelancer_profile.profile_image.url
        elif hasattr(user, 'client_profile') and user.client_profile.profile_image:
            return user.client_profile.profile_image.url
        else:
            return None  # or default image URL



class ChatDetailView(LoginRequiredMixin, View):
    def get(self, request, chat_id):
        chat = get_object_or_404(Chat, id=chat_id)
        # Ensure the user is a participant in the chat
        if request.user not in chat.participants.all():
            return redirect('chat:chat_list')
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
            return redirect('chat:chat_list')  # Redirect back to chat detail



from django.views.generic import ListView
from .models import CustomUser


class ClientListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'core/not usage pages/clients_list.html'

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


from django.db.models import Count


class StartChatView(LoginRequiredMixin, View):
    def get(self, request, username):
        # Retrieve the freelancer by username
        freelancer = get_object_or_404(CustomUser, username=username)

        # Check if there's an existing chat with exactly these two participants
        chat = Chat.objects.annotate(num_participants=Count('participants')).filter(num_participants=2,
                                                                                    participants=request.user).filter(
            participants=freelancer).first()

        if not chat:
            # If no chat exists, create a new one
            chat = Chat.objects.create()
            chat.participants.add(request.user, freelancer)
            chat.save()

        # Redirect to the chat detail view
        return redirect('chat:chat_detail', chat_id=chat.pk)


from django.contrib.auth.decorators import login_required


@login_required
def send_message(request, chat_id):
    if request.method == 'POST':
        chat = get_object_or_404(Chat, pk=chat_id)
        form = MessageForm(request.POST)

        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.chat = chat
            message.save()

        return redirect('chat:chat_list')
    else:
        return redirect('chat:chat_list')

from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Chat  # Import your Chat model
def chat_detail_ajax(request):
    chat_id = request.GET.get('chat_id')
    chat = Chat.objects.get(pk=chat_id)
    messages = chat.messages.all()  # Assuming you have a related_name 'messages' on your Chat model
    context = {'chat': chat, 'messages': messages}
    html = render_to_string('core/chat_detail.html', context, request=request)
    return HttpResponse(html)