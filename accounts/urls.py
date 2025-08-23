from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Custom password change views only
    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', views.CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
]
