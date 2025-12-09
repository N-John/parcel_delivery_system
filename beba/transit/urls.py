# urls.py

from django.urls import path
from . import views

app_name = "transit"

urlpatterns = [
    # Vehicles
    path('vehicles/', views.VehicleListView.as_view(), name='vehicle_list'),
    path('vehicles/add/', views.VehicleCreateView.as_view(), name='vehicle_add'),
    path('vehicles/<int:pk>/edit/', views.VehicleUpdateView.as_view(), name='vehicle_edit'),

    # Transit
    path('transit/', views.TransitListView.as_view(), name='transit_list'),
    path('transit/add/', views.TransitCreateView.as_view(), name='transit_add'),
    path('transit/<int:pk>/', views.TransitDetailView.as_view(), name='transit_detail'),

    # Delivery
    path('delivery/', views.DeliveryListView.as_view(), name='delivery_list'),
    path('delivery/add/', views.DeliveryCreateView.as_view(), name='delivery_add'),
    path('delivery/<int:pk>/', views.DeliveryDetailView.as_view(), name='delivery_detail'),
]