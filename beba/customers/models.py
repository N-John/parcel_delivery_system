from django.contrib.auth.models import User
from django.db import models


class Customer(models.Model):
    CUSTOMER_TYPES = [
        ("individual", "Individual"),
        ("business", "Business"),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPES, default="individual")

    # Address details
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Kenya")

    # Account details
    registered = models.BooleanField(default=True)  # False for guest pickups
    identification_number = models.CharField(max_length=50, blank=True)  # e.g. ID card/passport for verification
    created_at = models.DateTimeField(auto_now_add=True)

    user_account = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="customer_profile"
    )

    def __str__(self):
        return f"{self.name} ({'Registered' if self.registered else 'Guest'})"