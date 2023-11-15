from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    # Order views
    path('orders/', views.OrderListView.as_view(), name='orders_list'),
    path('orders/create/', views.OrderCreateView.as_view(), name='order_create'),
    path('orders/<slug:slug>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('orders/<slug:slug>/update/', views.OrderUpdateView.as_view(), name='order_update'),

    # Actions for orders
    path('orders/<int:order_id>/take/', views.TakeOrderView.as_view(), name='take_order'),
    path('orders/<int:order_id>/update_status/', views.UpdateOrderStatusView.as_view(), name='update_order_status'),

    # Freelancer-specific views
    path('freelancer/taken-orders/', views.TakenOrdersListView.as_view(), name='taken_orders_list'),
]
