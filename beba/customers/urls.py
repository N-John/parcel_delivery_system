# urls.py (app level)

from django.urls import path
from .views import (
    CustomerRegisterView, CustomerLoginView, CustomerLogoutView,
    CustomerProfileView, CustomerPasswordChangeView
)

app_name = "customers"

urlpatterns = [
    path('register/', CustomerRegisterView.as_view(), name='customer_register'),
    path('login/', CustomerLoginView.as_view(), name='customer_login'),
    path('logout/', CustomerLogoutView.as_view(), name='customer_logout'),
    path('profile/', CustomerProfileView.as_view(), name='customer_profile'),
    path('password/change/', CustomerPasswordChangeView.as_view(), name='customer_password_change'),
]