

from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect
from .models import Customer
from .forms import CustomerRegistrationForm, CustomerProfileForm  


# 1. Customer Registration (Create Account)
class CustomerRegisterView(CreateView):
    model = Customer
    form_class = CustomerRegistrationForm
    template_name = 'customers/register.html'
    success_url = reverse_lazy('customer_profile')  # Redirect to profile after registration

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object.user_account

        # Log the user in automatically after registration
        from django.contrib.auth import login
        login(self.request, user)

        messages.success(self.request, "Account created successfully! Welcome.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


# 2. Customer Login
class CustomerLoginView(LoginView):
    template_name = 'customers/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        messages.success(self.request, f"Welcome back, {self.request.user.customer_profile.name}!")
        return reverse_lazy('customer_profile')

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)


# 3. Customer Profile (View + Edit)
class CustomerProfileView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerProfileForm
    template_name = 'customers/profile.html'
    success_url = reverse_lazy('customer_profile')

    def get_object(self, queryset=None):
        # Ensure customers can only edit their own profile
        return self.request.user.customer_profile

    def form_valid(self, form):
        messages.success(self.request, "Your profile has been updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


# 4. Change Password
class CustomerPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = 'customers/password_change.html'
    success_url = reverse_lazy('customer_profile')

    def form_valid(self, form):
        messages.success(self.request, "Your password has been changed successfully.")
        return super().form_valid(form)


# 5. Logout (optional custom view)
class CustomerLogoutView(LogoutView):
    next_page = reverse_lazy('customer_login')

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "You have been logged out.")
        return super().dispatch(request, *args, **kwargs)