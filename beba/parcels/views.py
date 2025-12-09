from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.views import View
from orders.models import Item
from django.views.generic import ListView, DetailView
from .models import Parcel, ParcelHandover
from .forms import ParcelForm, ItemForm

class ParcelCreateView(View):
    def get(self, request):
        form = ParcelForm()
        return render(request, "parcels/parcel_form.html", {"form": form})

    def post(self, request):
        form = ParcelForm(request.POST)
        if form.is_valid():
            parcel = form.save(commit=False)
            parcel.created_by = request.user  # track who created
            parcel.save()
            return redirect("parcel_detail", pk=parcel.pk)
        return render(request, "parcels/parcel_form.html", {"form": form})


def add_item_to_parcel(request, parcel_id):
    parcel = get_object_or_404(Parcel, pk=parcel_id)

    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.parcel = parcel
            item.save()
            return redirect("parcel_detail", pk=parcel.pk)
    else:
        form = ItemForm()

    return render(request, "parcels/item_form.html", {"form": form, "parcel": parcel})


def record_handover(request, parcel_id):
    parcel = get_object_or_404(Parcel, pk=parcel_id)

    # Only staff can record handovers
    if not hasattr(request.user, "staff_profile"):
        return HttpResponseForbidden("Only staff can record handovers.")

    if request.method == "POST":
        from_staff = request.user.staff_profile
        to_staff_id = request.POST.get("to_staff_id")
        location_id = request.POST.get("location_id")
        handover_type = request.POST.get("handover_type")

        handover = ParcelHandover.objects.create(
            parcel=parcel,
            from_staff=from_staff,
            to_staff_id=to_staff_id,
            location_id=location_id,
            handover_type=handover_type,
            from_ack=True
        )
        return redirect("parcel_detail", pk=parcel.pk)

    return render(request, "parcels/handover_form.html", {"parcel": parcel})