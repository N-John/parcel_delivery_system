from django.db import models

class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ("truck", "Truck"),
        ("van", "Van"),
        ("bike", "Bike"),
        ("other", "Other"),
    ]

    plate_number = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    capacity_weight = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)  # kg
    capacity_volume = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)  # cubic meters
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.plate_number} ({self.get_type_display()})"
    
class TransitAssignment(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="assignments")
    driver = models.ForeignKey("staff.Staff", on_delete=models.CASCADE, related_name="driving_assignments")
    parcels = models.ManyToManyField("parcels.Parcel", related_name="transit_assignments")

    origin = models.ForeignKey("locations.Location", on_delete=models.SET_NULL, null=True, blank=True, related_name="assignments_origin")
    destination = models.ForeignKey("locations.Location", on_delete=models.SET_NULL, null=True, blank=True, related_name="assignments_destination")

    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ("scheduled", "Scheduled"),
        ("in_transit", "In Transit"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ], default="scheduled")

    def __str__(self):
        return f"{self.vehicle} assigned to {self.driver} ({self.status})"

class DeliveryAssignment(models.Model):
    parcel = models.ForeignKey("parcels.Parcel", on_delete=models.CASCADE, related_name="delivery_assignments")
    courier = models.ForeignKey("staff.Staff", on_delete=models.CASCADE, related_name="deliveries")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name="deliveries")

    origin = models.ForeignKey("locations.Location", on_delete=models.SET_NULL, null=True, blank=True, related_name="delivery_origin")
    destination_address = models.TextField()  # customer’s home address
    destination_city = models.CharField(max_length=100, blank=True)

    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=[
        ("assigned", "Assigned"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
        ("failed", "Failed Delivery"),
        ("returned", "Returned to Station/Hub"),
    ], default="assigned")

    requires_signature = models.BooleanField(default=False)
    signed_off = models.BooleanField(default=False)

    def __str__(self):
        return f"Delivery {self.parcel.tracking_number} by {self.courier}"

class DeliveryLog(models.Model):
    assignment = models.ForeignKey(DeliveryAssignment, on_delete=models.CASCADE, related_name="logs")
    status = models.CharField(max_length=30)  # e.g. "Out for Delivery", "Delivered", "Failed"
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)  # optional GPS or hub/station reference
    staff = models.ForeignKey("staff.Staff", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.assignment.parcel.tracking_number} - {self.status} at {self.timestamp}"
    
class TransitLog(models.Model):
    assignment = models.ForeignKey(TransitAssignment, on_delete=models.CASCADE, related_name="logs")
    location = models.ForeignKey("locations.Location", on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"TransitLog for {self.assignment.vehicle} at {self.timestamp}"
