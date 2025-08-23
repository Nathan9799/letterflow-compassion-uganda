from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Check if user must change password
            if request.user.must_change_password:
                # Allow access to password change page and logout
                allowed_paths = [
                    reverse('password_change'),
                    reverse('logout'),
                ]
                
                if request.path not in allowed_paths:
                    messages.warning(
                        request, 
                        'You must change your password before continuing.'
                    )
                    return redirect('password_change')
        
        response = self.get_response(request)
        return response
