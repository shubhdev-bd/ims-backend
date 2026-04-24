# from django.contrib import admin
# from .models import Device, Assignment, TicketRequest

# # @admin.register(Device)
# # class DeviceAdmin(admin.ModelAdmin):
# #     list_display = ['device_id', 'name', 'device_type', 'status', 'condition']
# #     list_filter = ['device_type', 'status', 'condition']
# #     search_fields = ['device_id', 'name', 'brand', 'model']

# @admin.register(Device)
# class DeviceAdmin(admin.ModelAdmin):
#     list_display = ['device_id', 'device_type', 'brand', 'model', 'status']
#     list_filter = ['device_type', 'brand']
#     search_fields = ['device_id', 'brand', 'model']
    
# @admin.register(Assignment)
# class AssignmentAdmin(admin.ModelAdmin):
#     list_display = ['device', 'employee', 'assigned_date', 'status']
#     list_filter = ['status', 'assigned_date']
#     search_fields = ['device__device_id', 'employee__email']

# @admin.register(TicketRequest)
# class TicketRequestAdmin(admin.ModelAdmin):
#     list_display = ['ticket_number', 'requested_by', 'ticket_type', 'priority', 'status']
#     list_filter = ['ticket_type', 'priority', 'status']
#     search_fields = ['ticket_number', 'subject']



from django.contrib import admin, messages
from django import forms
from django.shortcuts import render, redirect
from django.urls import path
import json

from .models import Device, Assignment, TicketRequest


# ✅ Form for upload
class JSONUploadForm(forms.Form):
    json_file = forms.FileField()


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['device_id', 'device_type', 'brand', 'model', 'status']
    list_filter = ['device_type', 'brand', 'status']
    search_fields = ['device_id', 'brand', 'model']

    change_list_template = "admin/device_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-json/', self.upload_json),
        ]
        return custom_urls + urls

    def upload_json(self, request):
        if request.method == "POST":
            form = JSONUploadForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES["json_file"]

                try:
                    data = json.load(file)
                except:
                    self.message_user(request, "Invalid JSON file", level=messages.ERROR)
                    return redirect("..")

                inventory = data.get("inventory", {})
                created_count = 0

                mapping = {
                    "laptops": "laptop",
                    "mouse": "mouse",
                    "keyboards": "keyboard",
                    "pc_setups": "pc",
                    "headphones": "headphone"
                }

                for key, device_type in mapping.items():
                    for item in inventory.get(key, []):
                        device_id = item.get("id")

                        if not device_id:
                            continue

                        # Skip duplicates
                        if Device.objects.filter(device_id=device_id).exists():
                            continue

                        brand = item.get("brand", "")
                        model = item.get("model", "")
                        name = f"{brand} {model}".strip() or device_type

                        specs = {
                            k: v for k, v in item.items()
                            if k not in ["id", "brand", "model"]
                        }

                        Device.objects.create(
                            device_id=device_id,
                            name=name,
                            device_type=device_type,
                            brand=brand,
                            model=model,
                            specifications=specs,
                            status="available",
                            created_by=request.user
                        )

                        created_count += 1

                self.message_user(
                    request,
                    f"{created_count} devices uploaded successfully",
                    level=messages.SUCCESS
                )

                return redirect("..")

        else:
            form = JSONUploadForm()

        return render(request, "admin/upload_json.html", {"form": form})
    

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['device', 'employee', 'assigned_date', 'status']
    list_filter = ['status', 'assigned_date']
    search_fields = ['device__device_id', 'employee__email']


@admin.register(TicketRequest)
class TicketRequestAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'requested_by', 'ticket_type', 'priority', 'status']
    list_filter = ['ticket_type', 'priority', 'status']
    search_fields = ['ticket_number', 'subject']