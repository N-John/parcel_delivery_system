import uuid
import datetime
from .models import ParcelHandover

def generate_tracking_number(prefix="PRC"):
    """
    Generate a unique tracking number for a parcel.
    Format: PRC-YYYYMMDD-XXXX
    """
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    random_str = uuid.uuid4().hex[:6].upper()
    return f"{prefix}-{date_str}-{random_str}"

def update_parcel_status(parcel, new_status, staff=None, note=""):
    """
    Update the status of a parcel and log the change.
    """
    parcel.status = new_status
    parcel.save()

    # Log the change
    parcel.logs.create(
        status=new_status,
        staff=staff,
        note=note
    )
    return parcel



def assign_parcel_handover(parcel, from_staff, to_staff, location, handover_type, note=""):
    """
    Create a handover record for a parcel.
    """
    handover = ParcelHandover.objects.create(
        parcel=parcel,
        from_staff=from_staff,
        to_staff=to_staff,
        location=location,
        handover_type=handover_type,
        note=note
    )
    return handover

from .models import Parcel
from parcels.utils import generate_tracking_number

def create_parcel(customer, origin, destination, weight=0.0, value=0.0, items=None):
    """
    Create a new parcel with optional items.
    """
    tracking_number = generate_tracking_number()
    parcel = Parcel.objects.create(
        customer=customer,
        origin=origin,
        destination=destination,
        weight=weight,
        value=value,
        tracking_number=tracking_number,
        status="created"
    )

    # Add items if provided
    if items:
        for item_data in items:
            parcel.items.create(**item_data)

    return parcel

def calculate_parcel_value(parcel):
    """
    Calculate the total declared value of items in a parcel.
    """
    total_value = sum(item.value * item.quantity for item in parcel.items.all() if item.value)
    return total_value

def is_parcel_deliverable(parcel):
    """
    Check if a parcel is ready for delivery.
    """
    return parcel.status in ["ready_for_delivery", "out_for_delivery"]

