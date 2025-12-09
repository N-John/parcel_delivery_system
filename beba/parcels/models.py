from django.db import models
from django.utils import timezone
import secrets


class Parcel(models.Model):
    STATUS_CHOICES = [
        ("packed", "Packed"),
        ("in_transit", "In Transit"),
        ("at_station", "At Pickup Station"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
        ("returned_station", "Returned to Pickup Station"),
        ("returned_warehouse", "Returned to Warehouse"),
        ("cancelled", "Cancelled"),
    ]
    PAYMENT_CHOICES = [
        ("online", "Online Payment"),
        ("pickup", "Pay on Pickup"),
        ("none", "Unpaid"),
    ]

    tracking_number = models.CharField(max_length=20, unique=True)
    sender_customer = models.ForeignKey("customers.Customer", on_delete=models.SET_NULL, null=True, blank=True, related_name="sent_parcels")
    sender_warehouse = models.ForeignKey("locations.Location", on_delete=models.SET_NULL, null=True, blank=True, related_name="outgoing_parcels")
    recipient = models.ForeignKey("customers.Customer", on_delete=models.SET_NULL, related_name="received_parcels",null=True, blank=True)

    origin = models.ForeignKey("locations.Location", on_delete=models.SET_NULL, null=True, blank=True,related_name='origin')
    destination_station = models.ForeignKey("locations.Location", on_delete=models.SET_NULL, null=True, blank=True,related_name='destination')
    home_delivery_location = models.TextField(null=True, blank=True)
    current_location = models.CharField(max_length=100, blank=True)

    weight = models.DecimalField(max_digits=8, decimal_places=2)
    dimensions = models.CharField(max_length=100, blank=True)
    fragile = models.BooleanField(default=False)
    requires_signature = models.BooleanField(default=False)

    expected_delivery_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=20, choices=[("standard","Standard"),("express","Express"),("overnight","Overnight")], default="standard")
    special_instructions = models.TextField(blank=True)

    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default="none")
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    extra_charges = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="packed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    station_arrival_time = models.DateTimeField(null=True, blank=True)
    pickup_code = models.CharField(max_length=10, unique=True, blank=True)

    def generate_pickup_code(self):
        self.pickup_code = secrets.token_hex(4).upper()  # e.g. "A1B2C3D4"
        self.save()
        return self.pickup_code

    def __str__(self):
        return f"Parcel {self.tracking_number} ({self.get_status_display()})"

class ReturnRequest(models.Model):
    """Staff or cariers can return tiems to where they are from"""

    RETURN_REASONS=[("delivery_refused","Customer refused delivery"),
            ("customer_unavailable","Customer not available"),
            ("wrong_address","Wrong address provided"),
            ("expired_window","Exceeded pickup window"),
            ('damaged_in_transit', "Damaged in transit"),
            ('expired', "Expired goods"),
            ('packaging_issue', "Packaging issue"),
            ('failed_delivery_attempt', "Failed delivery attempts"),
            ('restricted_item', "Restricted item"),
            ('lost_in_transit', "Lost in transit") ,
            ('customer_requested_return', "Return to sender requested")
    ]

    parcel = models.OneToOneField(Parcel, on_delete=models.CASCADE, related_name="return_request")
    reason = models.CharField(max_length=30, choices=RETURN_REASONS, default="failed_delivery_attempt")
    description = models.TextField(blank=True)  
    initiated_by = models.ForeignKey("staff.Staff", on_delete=models.SET_NULL, null=True, blank=True)
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    return_to_station = models.ForeignKey("locations.Location", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Return for {self.parcel.tracking_number} ({self.reason})"

class ParcelHandover(models.Model):
    HANDOVER_TYPES = [
        ("warehouse_to_driver", "Warehouse → Driver"),
        ("driver_to_warehouse", "Driver → Warehouse"),
        ("driver_to_station", "Driver → Pickup Station"),
        ("station_to_courier", "Station → Courier"),
        ("courier_to_customer", "Courier → Customer"),
        ("return_to_station", "Return → Pickup Station"),
        ("return_to_warehouse", "Return → Warehouse"),
        ("inter_warehouse", "Warehouse → Warehouse"),

    ]

    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name="handovers")

    # Who is handing over and who is receiving
    from_staff = models.ForeignKey("staff.Staff", on_delete=models.SET_NULL, null=True, blank=True, related_name="handover_from")
    to_staff = models.ForeignKey("staff.Staff", on_delete=models.SET_NULL, null=True, blank=True, related_name="handover_to")
    to_customer = models.ForeignKey("customers.Customer", on_delete=models.SET_NULL, null=True, blank=True, related_name="handover_customer")

    handover_type = models.CharField(max_length=30, choices=HANDOVER_TYPES)
    location = models.ForeignKey("locations.Location", on_delete=models.SET_NULL, null=True, blank=True, related_name="handovers")
    timestamp = models.DateTimeField(auto_now_add=True)

    # Acknowledgments
    from_ack = models.BooleanField(default=False)
    to_ack = models.BooleanField(default=False)

    note = models.TextField(blank=True)

    def __str__(self):
        return f"Handover {self.parcel.tracking_number} ({self.handover_type}) at {self.location}"
    
class ParcelExcange(models.Model):
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name="switches")
    from_recipient = models.ForeignKey("customers.Customer", on_delete=models.SET_NULL, null=True, blank=True, related_name="switches_from")
    to_recipient = models.ForeignKey("customers.Customer", on_delete=models.SET_NULL, null=True, blank=True, related_name="switches_to")
    from_station = models.ForeignKey("locations.Location", on_delete=models.SET_NULL, null=True, blank=True, related_name="switches_from")
    to_station = models.ForeignKey("locations.Location", on_delete=models.SET_NULL, null=True, blank=True, related_name="switches_to")
    switched_by = models.ForeignKey("staff.Staff", on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Switch for {self.parcel.tracking_number} at {self.timestamp}"

class ParcelLog(models.Model):
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, related_name="logs")
    status = models.CharField(max_length=30)
    location = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    staff = models.ForeignKey("staff.Staff", on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.parcel.tracking_number} - {self.status} at {self.timestamp}"

class ParcelPickup(models.Model):
    parcel = models.OneToOneField(Parcel, on_delete=models.CASCADE, related_name="pickup_event")

    # Option 1: Registered customer pickup
    customer = models.ForeignKey(
        "customers.Customer", on_delete=models.SET_NULL, null=True, blank=True, related_name="parcel_pickups"
    )

    # Option 2: Guest pickup using code
    pickup_code = models.CharField(max_length=10, blank=True)  # must match parcel.pickup_code
    guest_name = models.CharField(max_length=100, blank=True)
    guest_id = models.CharField(max_length=50, blank=True)  # optional ID card/passport

    # Staff verifying the pickup
    staff = models.ForeignKey("staff.Staff", on_delete=models.SET_NULL, null=True, blank=True)
    signed_off = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.customer:
            return f"Pickup for {self.parcel.tracking_number} by {self.customer.name}"
        elif self.guest_name:
            return f"Pickup for {self.parcel.tracking_number} by guest {self.guest_name}"
        return f"Pickup for {self.parcel.tracking_number}"
