
from django.contrib.auth.models import User
from django.db import models
from transit.models import Vehicle
from locations.models import Location

class Staff(models.Model):
    ROLE_CHOICES = [
        ("warehouse", "Warehouse Staff"),
        ("station", "Pickup Station Staff"),
        ("driver", "Driver"),
        ("courier", "Courier"),
        ("manager", "Management"),
        ("admin", "Administrator"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="staff_profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    employee_id = models.CharField(max_length=50, unique=True)
    assigned_vehicle = models.ForeignKey(
        Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_staff"
    )
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True, related_name="staff_members"
    )

    date_joined = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} ({self.role()})"