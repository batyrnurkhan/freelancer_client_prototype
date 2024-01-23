from django.contrib import admin
from django.forms import ModelForm
from django.contrib.admin.widgets import FilteredSelectMultiple
from .models import Order

class OrderAdminForm(ModelForm):
    class Meta:
        model = Order
        fields = '__all__'
        widgets = {
            'skills': FilteredSelectMultiple("Skills", is_stacked=False),
        }

class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm

admin.site.register(Order, OrderAdmin)
