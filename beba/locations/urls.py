# urls.py

from django.urls import path
from . import views

app_name = "locations"

urlpatterns = [
    path('', views.LocationListView.as_view(), name='location_list'),
    path('create/', views.LocationCreateView.as_view(), name='location_create'),
    path('<int:pk>/update/', views.LocationUpdateView.as_view(), name='location_update'),
    path('<int:pk>/assign-staff/', views.AssignStaffToLocationView.as_view(), name='assign_staff'),
]