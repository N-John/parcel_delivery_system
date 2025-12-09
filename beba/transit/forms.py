# forms.py

from django import forms
from .models import Vehicle, TransitAssignment, DeliveryAssignment, TransitLog, DeliveryLog
from staff.models import Staff
from locations.models import Location

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['plate_number', 'type', 'capacity_weight', 'capacity_volume', 'active']
        widgets = {
            'capacity_weight': forms.NumberInput(attrs={'step': '0.01'}),
            'capacity_volume': forms.NumberInput(attrs={'step': '0.01'}),
        }

class TransitAssignmentForm(forms.ModelForm):
    class Meta:
        model = TransitAssignment
        fields = [
            'vehicle', 'driver', 'parcels', 'origin', 'destination',
            'departure_time', 'arrival_time', 'status'
        ]
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'parcels': forms.SelectMultiple(attrs={'size': 10}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter drivers to those with role "driver" or "courier"
        self.fields['driver'].queryset = Staff.objects.filter(
            role__in=['driver', 'courier'], active=True
        )
        self.fields['origin'].queryset = Location.objects.filter(active=True)
        self.fields['destination'].queryset = Location.objects.filter(active=True)

class DeliveryAssignmentForm(forms.ModelForm):
    class Meta:
        model = DeliveryAssignment
        fields = [
            'parcel', 'courier', 'vehicle', 'origin', 'destination_address',
            'destination_city', 'departure_time', 'arrival_time', 'status',
            'requires_signature'
        ]
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'destination_address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['courier'].queryset = Staff.objects.filter(
            role__in=['courier', 'driver'], active=True
        )
        self.fields['origin'].queryset = Location.objects.filter(active=True)

class TransitLogForm(forms.ModelForm):
    class Meta:
        model = TransitLog
        fields = ['location', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 2}),
        }

class DeliveryLogForm(forms.ModelForm):
    class Meta:
        model = DeliveryLog
        fields = ['status', 'note', 'location']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 2}),
            'status': forms.Select(choices=[
                ("Out for Delivery", "Out for Delivery"),
                ("Delivered", "Delivered"),
                ("Failed", "Failed Delivery"),
                ("Returned to Station/Hub", "Returned"),
            ])
        }