from django.shortcuts import render
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.urls import reverse_lazy

# Create your views here.

class CustomPasswordChangeView(PasswordChangeView):
    """Custom password change view that redirects to login page"""
    success_url = reverse_lazy('login')
    template_name = 'registration/password_change_form.html'

class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    """Custom password change done view that redirects to login page"""
    template_name = 'registration/password_change_done.html'
    
    def get_success_url(self):
        """Redirect to login page after password change"""
        return reverse_lazy('login')
