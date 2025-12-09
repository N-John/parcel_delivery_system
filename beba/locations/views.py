# views.py

from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.forms import modelformset_factory
from .models import Location,Warehouse,Hub,PickupStation
from .forms import (
    LocationForm, WarehouseForm, PickupStationForm, HubForm, StaffFormSet
)
from staff.models import Staff 

class LocationPermissionMixin(UserPassesTestMixin):
    """Reusable mixin for location management permissions"""
    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        try:
            return user.staff_profile.role in ("manager", "admin") and user.staff_profile.active
        except AttributeError:
            return False

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to manage locations.")
        return redirect('staff:staff_list')  # Or home page

# 1. List All Locations
class LocationListView(LoginRequiredMixin, LocationPermissionMixin, ListView):
    model = Location
    template_name = 'locations/location_list.html'
    context_object_name = 'locations'
    paginate_by = 20
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by type if requested
        location_type = self.request.GET.get('type')
        if location_type:
            queryset = queryset.filter(location_type=location_type)
        # Show only active by default
        if not self.request.GET.get('show_all'):
            queryset = queryset.filter(active=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location_types'] = Location.LOCATION_TYPES
        context['selected_type'] = self.request.GET.get('type')
        context['show_all'] = self.request.GET.get('show_all', 'false').lower() == 'true'
        return context

# 2. Create Location (handles subclass creation)
class LocationCreateView(LoginRequiredMixin, LocationPermissionMixin, CreateView):
    model = Location
    form_class = LocationForm
    template_name = 'locations/location_form.html'
    success_url = reverse_lazy('locations:location_list')

    def get_success_url(self):
        messages.success(self.request, f"Location '{self.object.name}' created successfully.")
        return super().get_success_url()

    def form_valid(self, form):
        self.object = form.save()
        location_type = form.cleaned_data['location_type']

        # Create subclass instance based on type
        if location_type == 'warehouse':
            Warehouse.objects.create(location=self.object)
        elif location_type == 'pickup_station':
            PickupStation.objects.create(location=self.object)
        elif location_type == 'hub':
            Hub.objects.create(location=self.object)

        return super().form_valid(form)

# 3. Update Location (handles subclass fields)
class LocationUpdateView(LoginRequiredMixin, LocationPermissionMixin, UpdateView):
    model = Location
    form_class = LocationForm
    template_name = 'locations/location_form.html'
    success_url = reverse_lazy('locations:location_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Add subclass form based on type
        if self.object.location_type == 'warehouse' and hasattr(self.object, 'warehouse_location'):
            kwargs['subform'] = WarehouseForm(instance=self.object.warehouse_location)
        elif self.object.location_type == 'pickup_station' and hasattr(self.object, 'station_location'):
            kwargs['subform'] = PickupStationForm(instance=self.object.station_location)
        elif self.object.location_type == 'hub' and hasattr(self.object, 'location'):  # Note: related_name="Location" might need fix
            kwargs['subform'] = HubForm(instance=self.object.location)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'subform' in self.get_form_kwargs():
            context['subform'] = self.get_form_kwargs()['subform']
        # Staff assignment formset
        if self.request.POST:
            context['staff_formset'] = StaffFormSet(self.request.POST, instance=self.object)
        else:
            context['staff_formset'] = StaffFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        staff_formset = context['staff_formset']
        if staff_formset.is_valid():
            self.object = form.save()
            staff_formset.save()
            # Save subform if present
            if 'subform' in context and context['subform'].is_valid():
                context['subform'].save()
            messages.success(self.request, f"Location '{self.object.name}' updated successfully.")
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

# 4. Assign Staff to Location (simple view for bulk assignment)
class AssignStaffToLocationView(LoginRequiredMixin, LocationPermissionMixin, UpdateView):
    model = Location
    fields = []  # No fields, just use formset
    template_name = 'locations/assign_staff.html'
    success_url = reverse_lazy('locations:location_list')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        formset = StaffFormSet(queryset=Staff.objects.all(), instance=self.object)
        return self.render_to_response(self.get_context_data(formset=formset))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        formset = StaffFormSet(request.POST, instance=self.object)
        if formset.is_valid():
            formset.save()
            messages.success(request, f"Staff assigned to '{self.object.name}' successfully.")
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(formset=formset))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'formset' not in context:
            context['formset'] = StaffFormSet(queryset=Staff.objects.filter(active=True), instance=self.object)
        context['location'] = self.object
        return context