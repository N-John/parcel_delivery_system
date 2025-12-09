from django.urls import path
from . import views

app_name = "staff"  # Optional but recommended: enables reverse URLs like 'staff:add_staff'

urlpatterns = [
    path('', views.StaffListView.as_view(), name='staff_list'),
    path('staff/add/', views.AddStaffView.as_view(), name='add_staff'),
    path('staff/<int:pk>/edit/', views.EditStaffView.as_view(), name='edit_staff'),
]