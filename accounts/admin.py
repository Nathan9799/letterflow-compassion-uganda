from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User


class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.Role.choices)
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'role', 'first_name', 'last_name')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    model = User
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'must_change_password')
    list_filter = ('role', 'is_active', 'must_change_password')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Password Change', {'fields': ('must_change_password',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # New user
            obj.must_change_password = True
        super().save_model(request, obj, form, change)
