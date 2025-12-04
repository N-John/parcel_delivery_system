from django.db import models
from django.utils import timezone

class Invoice(models.Model):
    STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
        ("cancelled", "Cancelled"),
    ]

    invoice_number = models.CharField(max_length=20, unique=True)
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="invoices", null=True, blank=True)
    parcel = models.ForeignKey("parcels.Parcel", on_delete=models.SET_NULL, null=True, blank=True, related_name="invoices")

    customer = models.ForeignKey("customers.Customer", on_delete=models.SET_NULL, null=True, related_name="invoices")

    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="unpaid")

    issue_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} ({self.get_status_display()})"

class Payment(models.Model):
    METHOD_CHOICES = [
        ("card", "Card"),
        ("mobile_money", "Mobile Money"),
        ("mpesa", "Mpesa"),
        ("bank_transfer", "Bank Transfer"),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    customer = models.ForeignKey("customers.Customer", on_delete=models.SET_NULL, null=True, related_name="payments")

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    reference_code = models.CharField(max_length=50, blank=True)  # e.g. transaction ID
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Payment {self.amount} via {self.get_method_display()} for {self.invoice.invoice_number}"

class Refund(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="refunds")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    customer = models.ForeignKey("customers.Customer", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Refund {self.amount} for Payment {self.payment.id}"
