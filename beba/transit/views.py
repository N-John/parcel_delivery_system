# views.py

from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect

from .models import Vehicle, TransitAssignment, DeliveryAssignment
from .forms import (
    VehicleForm, TransitAssignmentForm, DeliveryAssignmentForm,
    TransitLogForm, DeliveryLogForm
)

class TransitPermissionMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        try:
            return user.staff_profile.role in ("manager", "admin") and user.staff_profile.active
        except:
            return False

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to manage transit.")
        return redirect('locations:location_list')

# --- Vehicle Management ---
class VehicleListView(LoginRequiredMixin, TransitPermissionMixin, ListView):
    model = Vehicle
    template_name = 'transit/vehicle_list.html'
    context_object_name = 'vehicles'

class VehicleCreateView(LoginRequiredMixin, TransitPermissionMixin, CreateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'transit/vehicle_form.html'
    success_url = reverse_lazy('transit:vehicle_list')
    def form_valid(self, form):
        messages.success(self.request, f"Vehicle {form.instance.plate_number} added.")
        return super().form_valid(form)

class VehicleUpdateView(LoginRequiredMixin, TransitPermissionMixin, UpdateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'transit/vehicle_form.html'
    success_url = reverse_lazy('transit:vehicle_list')

# --- Transit Assignments ---
class TransitListView(LoginRequiredMixin, TransitPermissionMixin, ListView):
    model = TransitAssignment
    template_name = 'transit/transit_list.html'
    context_object_name = 'assignments'
    ordering = ['-departure_time']

class TransitCreateView(LoginRequiredMixin, TransitPermissionMixin, CreateView):
    model = TransitAssignment
    form_class = TransitAssignmentForm
    template_name = 'transit/transit_form.html'
    success_url = reverse_lazy('transit:transit_list')

    def form_valid(self, form):
        messages.success(self.request, "Transit assignment created.")
        return super().form_valid(form)

class TransitDetailView(LoginRequiredMixin, TransitPermissionMixin, DetailView):
    model = TransitAssignment
    template_name = 'transit/transit_detail.html'
    context_object_name = 'assignment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['log_form'] = TransitLogForm(self.request.POST)
        else:
            context['log_form'] = TransitLogForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        log_form = TransitLogForm(request.POST)
        if log_form.is_valid():
            log = log_form.save(commit=False)
            log.assignment = self.object
            log.save()
            messages.success(request, "Transit log added.")
            return redirect('transit:transit_detail', pk=self.object.pk)
        return self.render_to_response(self.get_context_data(log_form=log_form))

# --- Delivery Assignments ---
class DeliveryListView(LoginRequiredMixin, TransitPermissionMixin, ListView):
    model = DeliveryAssignment
    template_name = 'transit/delivery_list.html'
    context_object_name = 'deliveries'
    ordering = ['-departure_time']

class DeliveryCreateView(LoginRequiredMixin, TransitPermissionMixin, CreateView):
    model = DeliveryAssignment
    form_class = DeliveryAssignmentForm
    template_name = 'transit/delivery_form.html'
    success_url = reverse_lazy('transit:delivery_list')

    def form_valid(self, form):
        messages.success(self.request, f"Delivery for parcel {form.instance.parcel.tracking_number} assigned.")
        return super().form_valid(form)

class DeliveryDetailView(LoginRequiredMixin, TransitPermissionMixin, DetailView):
    model = DeliveryAssignment
    template_name = 'transit/delivery_detail.html'
    context_object_name = 'delivery'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['log_form'] = DeliveryLogForm(self.request.POST)
        else:
            context['log_form'] = DeliveryLogForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        log_form = DeliveryLogForm(request.POST)
        if log_form.is_valid():
            log = log_form.save(commit=False)
            log.assignment = self.object
            log.staff = request.user.staff_profile if hasattr(request.user, 'staff_profile') else None
            log.save()
            # Auto-update status if delivered
            if log.status == "Delivered":
                self.object.status = "delivered"
                self.object.arrival_time = log.timestamp
                self.object.signed_off = self.object.requires_signature
                self.object.save()
            messages.success(request, "Delivery log added.")
            return redirect('transit:delivery_detail', pk=self.object.pk)
        return self.render_to_response(self.get_context_data(log_form=log_form))