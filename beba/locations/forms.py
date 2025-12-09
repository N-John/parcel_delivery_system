# forms.py

from django import forms
from django.forms import inlineformset_factory
from .models import Location, Warehouse, PickupStation, Hub
from staff.models import Staff  # Adjust import as needed

class LocationForm(forms.ModelForm):
    """Base form for Location creation/editing"""
    class Meta:
        model = Location
        fields = [
            'name', 'location_tag', 'location_type', 'address', 'city', 'region',
            'country', 'latitude', 'longitude', 'active'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'location_type': forms.Select(choices=Location.LOCATION_TYPES),
            'latitude': forms.NumberInput(attrs={'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'step': 'any'}),
        }

# Subclass-specific forms (for editing)
class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['capacity', 'has_cold_storage', 'operating_hours', 'manager', 'contact_number']
        widgets = {
            'operating_hours': forms.TextInput(attrs={'placeholder': 'e.g., Mon-Sat 8am-8pm'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
        }

class PickupStationForm(forms.ModelForm):
    class Meta:
        model = PickupStation
        fields = ['opening_hours', 'max_storage_days', 'contact_number', 'has_lockers', 'station_manager']
        widgets = {
            'opening_hours': forms.TextInput(attrs={'placeholder': 'e.g., Mon-Fri 9am-6pm'}),
            'station_manager': forms.Select(attrs={'class': 'form-control'}),
        }

class HubForm(forms.ModelForm):
    class Meta:
        model = Hub
        fields = ['capacity', 'operating_hours', 'manager', 'contact_number', 'connected_routes', 'vehicle_parking_capacity']
        widgets = {
            'operating_hours': forms.TextInput(attrs={'placeholder': 'e.g., 24/7'}),
            'connected_routes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'e.g., Nairobi → Mombasa'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
        }

# Staff Assignment Formset (for ManyToMany)
StaffFormSet = inlineformset_factory(
    Location, Staff, fields=['id'], extra=0, can_delete=True,
    widgets={'id': forms.HiddenInput()}
)