# in listing/urls.py

from django.urls import path
from . import views
from .views import OrderListView, OrderCreateView, OrderDetailView
app_name = 'listings'
urlpatterns = [
    path('orders/', OrderListView.as_view(), name='orders_list'),
    path('orders/<slug:slug>/', OrderDetailView.as_view(), name='order_detail'),
    path('create/', OrderCreateView.as_view(), name='order_create'),  # Create a new order
    # path('<slug:slug>/', views.OrderDetailView.as_view(), name='order_detail'),  # View order details by slug
    # # Add any additional URLs you need for your application
    # path('jobs/', JobListView.as_view(), name='job_list'),
    # path('jobs/create/', JobCreateView.as_view(), name='job_create'),
    # path('jobs/<int:pk>/', JobDetailView.as_view(), name='job_detail'),
    # path('jobs/<int:pk>/update/', JobUpdateView.as_view(), name='job_update'),
]