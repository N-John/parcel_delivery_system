from django.db import models

class Location(models.Model):
    LOCATION_TYPES = [
        ("warehouse", "Warehouse"),
        ("pickup_station", "Pickup Station"),
        ("hub", "Transit Hub"),
        ("office", "Company Office"),
        ("custom", "Custom Location"),
    ]

    name = models.CharField(max_length=100)
    location_tag= models.CharField(max_length=20,unique=True)
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPES)
    address = models.TextField()
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Kenya")  # adjust default as needed
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    staff = models.ManyToManyField("staff.Staff", related_name="locations", blank=True)

    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_location_type_display()})"

class Warehouse(Location):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True, related_name="warehouse_location")
    capacity = models.IntegerField(default=0)  # max parcels it can store
    has_cold_storage = models.BooleanField(default=False)
    operating_hours = models.CharField(max_length=100, blank=True)  # e.g. "Mon-Sat 8am-8pm"
    manager = models.ForeignKey("staff.Staff", on_delete=models.SET_NULL, null=True, blank=True, related_name="managed_warehouses")
    contact_number = models.CharField(max_length=20, blank=True)

class PickupStation(Location):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True, related_name="station_location")
    opening_hours = models.CharField(max_length=100, blank=True)  # e.g. "Mon-Fri 9am-6pm"
    max_storage_days = models.IntegerField(default=7)  # how long parcels can stay before charges
    contact_number = models.CharField(max_length=20, blank=True)
    has_lockers = models.BooleanField(default=False)  # automated lockers for self-service pickup
    station_manager = models.ForeignKey("staff.Staff", on_delete=models.SET_NULL, null=True, blank=True, related_name="managed_stations")

class Hub(Location):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True, related_name="Location")
    capacity = models.IntegerField(default=0)
    operating_hours = models.CharField(max_length=100, blank=True)
    manager = models.ForeignKey("staff.Staff", on_delete=models.SET_NULL, null=True, blank=True, related_name="managed_hubs")
    contact_number = models.CharField(max_length=20, blank=True)
    connected_routes = models.TextField(blank=True)  # e.g. "Nairobi → Mombasa, Nairobi → Kisumu"
    vehicle_parking_capacity = models.IntegerField(default=0)  # number of trucks/vans it can host