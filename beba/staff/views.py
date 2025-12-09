from django.views.generic import CreateView,ListView,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from .form import StaffCreationForm,StaffEditForm
from .models import Staff

class EditStaffView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Staff
    form_class = StaffEditForm
    template_name = "staff/edit_staff.html"
    success_url = reverse_lazy("staff_list")  

    def test_func(self):
        """Only managers, admins, or superusers can edit staff"""
        user = self.request.user
        if user.is_superuser:
            return True
        try:
            return user.staff_profile.role in ("manager", "admin") and user.staff_profile.active
        except AttributeError:
            return False

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to edit staff members.")
        return super().handle_no_permission()

    def form_valid(self, form):
        messages.success(self.request, f"Staff member '{self.object.user.username}' updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['staff_user'] = self.object.user  # Pass the linked User for display
        return context

class AddStaffView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    form_class = StaffCreationForm
    template_name = "staff/add_staff.html"
    success_url = reverse_lazy("staff_list")  

    def test_func(self):
        """
        Only allow users whose Staff role is 'manager' or 'admin' (or superusers).
        """
        user = self.request.user
        if user.is_superuser:
            return True
        try:
            # Check if the user has a Staff profile and correct role
            return user.staff_profile.role in ("manager", "admin") and user.staff_profile.active
        except AttributeError:
            # User has no staff profile
            return False

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to add staff members.")
        return super().handle_no_permission()

    def form_valid(self, form):
        response = super().form_valid(form)  # Saves the User first

        # Now update the Staff instance with created_by
        staff_profile = self.object.staff_profile  # The newly created Staff instance
        staff_profile.created_by = self.request.user
        staff_profile.save()

        messages.success(self.request, f"Staff member '{self.object.username}' added successfully.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class StaffListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Staff
    template_name = "staff/list_staff.html"  
    context_object_name = "staff_members"    
    paginate_by = 20                         
    ordering = ['-date_joined']              

    def test_func(self):
        """Only managers, admins, or superusers can view the staff list"""
        user = self.request.user
        if user.is_superuser:
            return True
        try:
            return user.staff_profile.role in ("manager", "admin") and user.staff_profile.active
        except AttributeError:
            return False

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to view the staff list.")
        return super().handle_no_permission()

    def get_queryset(self):
        """Show only active staff by default. Managers/admins can optionally see all."""
        queryset = super().get_queryset()
        
        # Optional: Add a query param to show inactive staff (e.g., ?show_all=true)
        show_all = self.request.GET.get('show_all', 'false').lower() == 'true'
        
        if not show_all:
            queryset = queryset.filter(active=True)
        
        # Optional: Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(employee_id__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(role__icontains=search_query)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['show_all'] = self.request.GET.get('show_all', 'false').lower() == 'true'
        return context

