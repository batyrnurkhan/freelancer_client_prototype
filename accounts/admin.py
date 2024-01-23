from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, Profile, FreelancerProfile, ClientProfile, Skill

class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active',)
    list_filter = ('username', 'email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'user_type', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'user_type', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name',)
    ordering = ('username', 'email',)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'location', 'birth_date')

class FreelancerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'portfolio')

class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name')

class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Fields to display in the skill list view
    search_fields = ('name',)  # Fields to search in the skill list view
    ordering = ('name',)  # Default ordering

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(FreelancerProfile, FreelancerProfileAdmin)
admin.site.register(ClientProfile, ClientProfileAdmin)
admin.site.register(Skill, SkillAdmin)