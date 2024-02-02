from django.urls import path
from .views import SignUpView, SignInView, FreelancerProfileUpdateView, ProfileDetailView, FreelancerListView, LogoutView, \
    FreelancerDetailView, ClientListView, ClientDetailView, activate_account, skill_search, OrderListView, \
    update_client_profile
from django.contrib.auth import views as auth_views
from django.urls import path
from .views import search_freelancers

app_name = 'accounts'

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('profile/edit/', FreelancerProfileUpdateView.as_view(), name='edit_profile'),
    path('profile/', ProfileDetailView.as_view(), name='profile_detail'),
    path('freelancers/', FreelancerListView.as_view(), name='freelancer-list'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('freelancers/<int:pk>/', FreelancerDetailView.as_view(), name='freelancer_detail'),
    path('clients/', ClientListView.as_view(), name='client-list'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client_detail'),
    path('activate/<str:token>/', activate_account, name='activate'),
    path('search/', search_freelancers, name='your_search_view_url_name'),
    path('skill/', skill_search, name='skill_search'),
    path('orders/', OrderListView.as_view(), name='name_of_order_list_view'),
    path('profile/update/', update_client_profile, name='update_client_profile'),
]
