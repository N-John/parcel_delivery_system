from django.db import models
from django.utils import timezone

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("ready_for_dispatch", "Ready for Dispatch"),
        ("in_transit", "In Transit"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_CHOICES = [
        ("online", "Online Payment"),
        ("pickup", "Pay on Pickup"),
        ("none", "Unpaid"),
    ]

    order_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey("customers.Customer", on_delete=models.SET_NULL, null=True, related_name="orders")

    parcels = models.ManyToManyField("parcels.Parcel", related_name="orders")

    # Payment
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default="none")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    extra_charges = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    special_instructions = models.TextField(blank=True)

    def calculate_total(self):
        """Recalculate total amount including delivery fee and extra charges."""
        parcel_fees = sum(parcel.delivery_fee for parcel in self.parcels.all())
        self.total_amount = parcel_fees + self.delivery_fee + self.extra_charges
        self.save()

    def __str__(self):
        return f"Order {self.order_number} ({self.status})"

class Item(models.Model):
    CATEGORY_CHOICES = [
        ("electronics", "Electronics"),
        ("clothing", "Clothing"),
        ("documents", "Documents"),
        ("food", "Food"),
        ("fragile", "Fragile Goods"),
        ("other", "Other"),
    ]

    parcel = models.ForeignKey("parcels.Parcel", on_delete=models.CASCADE, related_name="items")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)

    name = models.CharField(max_length=100)  # e.g. "Smartphone", "Shoes"
    description = models.TextField(blank=True)  # optional details
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="other")

    quantity = models.PositiveIntegerField(default=1)
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)  # per item
    value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # monetary value

    fragile = models.BooleanField(default=False)
    requires_signature = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (x{self.quantity}) in Parcel {self.parcel.tracking_number}"