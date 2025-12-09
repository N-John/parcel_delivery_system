# admin.py
from django.contrib import admin
from .models import Staff
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "employee_id", "created_by", "date_joined")
    readonly_fields = ("created_by", "date_joined")