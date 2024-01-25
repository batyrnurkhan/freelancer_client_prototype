
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import IndexView
from django.conf.urls import handler404
handler404 = 'core.views.custom_404_view'
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('admin/clearcache/', include('clearcache.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('listings/', include('listings.urls')),
    path('chat/', include(('chat.urls', 'chat'), namespace ='chat')),

    # Password reset links (ref: https://github.com/django/django/blob/main/django/contrib/auth/views.py)
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='core/password_reset/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='core/password_reset/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='core/password_reset/password_reset_complete.html'), name='password_reset_complete'),

    #DRF


    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)