from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import Staff,Vehicle, Location


# forms.py

from django import forms
from .models import Staff, Vehicle, Location

class StaffEditForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = [
            'role',
            'phone',
            'employee_id',
            'assigned_vehicle',
            'location',
            'active',
        ]
        widgets = {
            'role': forms.Select(choices=Staff.ROLE_CHOICES),
            'assigned_vehicle': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'role': 'Role',
            'phone': 'Phone Number',
            'employee_id': 'Employee ID',
            'assigned_vehicle': 'Assigned Vehicle',
            'location': 'Assigned Location',
            'active': 'Active Status',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional: Improve queryset or add empty labels
        self.fields['assigned_vehicle'].queryset = Vehicle.objects.all()
        self.fields['assigned_vehicle'].empty_label = "No vehicle assigned"
        self.fields['location'].queryset = Location.objects.all()
        self.fields['location'].empty_label = "No location assigned"

        
class StaffCreationForm(UserCreationForm):
    """
    A form to create a new User and associated Staff profile in one step.
    Only accessible to managers/admins (enforce in view with permissions).
    """
    # User fields
    username = forms.CharField(max_length=150, help_text="Required. 150 characters or fewer.")
    email = forms.EmailField(required=True)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    # Staff profile fields
    role = forms.ChoiceField(choices=Staff.ROLE_CHOICES)
    phone = forms.CharField(max_length=20, required=False)
    employee_id = forms.CharField(max_length=50)
    assigned_vehicle = forms.ModelChoiceField(
        queryset=Vehicle.objects.all(),
        required=False,
        blank=True,
        empty_label="None"
    )
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        blank=True,
        empty_label="None"
    )
    active = forms.BooleanField(initial=True, required=False)

    class Meta:
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email required in the form display
        self.fields['email'].required = True

    def save(self, commit=True):
        # First save the User (with hashed password handled by UserCreationForm)
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        # Staff users need is_staff=True to access admin if desired
        user.is_staff = True  # Adjust based on your needs (e.g., only for certain roles)
        if commit:
            user.save()

            # Now create the Staff profile linked to this user
            Staff.objects.create(
                user=user,
                role=self.cleaned_data["role"],
                phone=self.cleaned_data["phone"],
                employee_id=self.cleaned_data["employee_id"],
                assigned_vehicle=self.cleaned_data["assigned_vehicle"],
                location=self.cleaned_data["location"],
                active=self.cleaned_data["active"],
            )
        return user