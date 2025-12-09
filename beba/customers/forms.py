
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Customer


class CustomerRegistrationForm(UserCreationForm):
    # Customer fields
    name = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=20, required=False)
    email = forms.EmailField(required=False)
    customer_type = forms.ChoiceField(choices=Customer.CUSTOMER_TYPES, required=True)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    city = forms.CharField(max_length=100, required=False)
    region = forms.CharField(max_length=100, required=False)
    identification_number = forms.CharField(max_length=50, required=False)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()

            # Create linked Customer profile
            Customer.objects.create(
                user_account=user,
                name=self.cleaned_data['name'],
                phone=self.cleaned_data['phone'],
                email=self.cleaned_data['email'],
                customer_type=self.cleaned_data['customer_type'],
                address=self.cleaned_data['address'],
                city=self.cleaned_data['city'],
                region=self.cleaned_data['region'],
                identification_number=self.cleaned_data['identification_number'],
                registered=True
            )
        return user


class CustomerProfileForm(forms.ModelForm):
    # Allow updating core User fields too
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = Customer
        fields = [
            'name', 'phone', 'email', 'customer_type',
            'address', 'city', 'region', 'country',
            'identification_number'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'customer_type': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-fill User fields
        if self.instance.user_account:
            self.fields['first_name'].initial = self.instance.user_account.first_name
            self.fields['last_name'].initial = self.instance.user_account.last_name
            self.fields['email'].initial = self.instance.user_account.email

    def save(self, commit=True):
        customer = super().save(commit=False)
        user = customer.user_account

        if user:
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            if commit:
                user.save()

        if commit:
            customer.save()
        return customer