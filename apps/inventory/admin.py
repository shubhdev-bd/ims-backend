# # from django.contrib import admin
# # from .models import Device, Assignment, TicketRequest

# # # @admin.register(Device)
# # # class DeviceAdmin(admin.ModelAdmin):
# # #     list_display = ['device_id', 'name', 'device_type', 'status', 'condition']
# # #     list_filter = ['device_type', 'status', 'condition']
# # #     search_fields = ['device_id', 'name', 'brand', 'model']

# # @admin.register(Device)
# # class DeviceAdmin(admin.ModelAdmin):
# #     list_display = ['device_id', 'device_type', 'brand', 'model', 'status']
# #     list_filter = ['device_type', 'brand']
# #     search_fields = ['device_id', 'brand', 'model']

# # @admin.register(Assignment)
# # class AssignmentAdmin(admin.ModelAdmin):
# #     list_display = ['device', 'employee', 'assigned_date', 'status']
# #     list_filter = ['status', 'assigned_date']
# #     search_fields = ['device__device_id', 'employee__email']

# # @admin.register(TicketRequest)
# # class TicketRequestAdmin(admin.ModelAdmin):
# #     list_display = ['ticket_number', 'requested_by', 'ticket_type', 'priority', 'status']
# #     list_filter = ['ticket_type', 'priority', 'status']
# #     search_fields = ['ticket_number', 'subject']


# from django.contrib import admin, messages
# from django import forms
# from django.shortcuts import render, redirect
# from django.urls import path
# import json

# from .models import Device, Assignment, TicketRequest, InventoryAsset


# # ✅ Form for upload
# class JSONUploadForm(forms.Form):
#     json_file = forms.FileField()


# @admin.register(Device)
# class DeviceAdmin(admin.ModelAdmin):
#     list_display = ['device_id', 'device_type', 'brand', 'model', 'status']
#     list_filter = ['device_type', 'brand', 'status']
#     search_fields = ['device_id', 'brand', 'model']

#     change_list_template = "admin/device_changelist.html"

#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('upload-json/', self.upload_json),
#         ]
#         return custom_urls + urls

#     def upload_json(self, request):
#         if request.method == "POST":
#             form = JSONUploadForm(request.POST, request.FILES)
#             if form.is_valid():
#                 file = request.FILES["json_file"]

#                 try:
#                     data = json.load(file)
#                 except:
#                     self.message_user(request, "Invalid JSON file", level=messages.ERROR)
#                     return redirect("..")

#                 inventory = data.get("inventory", {})
#                 created_count = 0

#                 mapping = {
#                     "laptops": "laptop",
#                     "mouse": "mouse",
#                     "keyboards": "keyboard",
#                     "pc_setups": "pc",
#                     "headphones": "headphone"
#                 }

#                 for key, device_type in mapping.items():
#                     for item in inventory.get(key, []):
#                         device_id = item.get("id")

#                         if not device_id:
#                             continue

#                         # Skip duplicates
#                         if Device.objects.filter(device_id=device_id).exists():
#                             continue

#                         brand = item.get("brand", "")
#                         model = item.get("model", "")
#                         name = f"{brand} {model}".strip() or device_type

#                         specs = {
#                             k: v for k, v in item.items()
#                             if k not in ["id", "brand", "model"]
#                         }

#                         Device.objects.create(
#                             device_id=device_id,
#                             name=name,
#                             device_type=device_type,
#                             brand=brand,
#                             model=model,
#                             specifications=specs,
#                             status="available",
#                             created_by=request.user
#                         )

#                         created_count += 1

#                 self.message_user(
#                     request,
#                     f"{created_count} devices uploaded successfully",
#                     level=messages.SUCCESS
#                 )

#                 return redirect("..")

#         else:
#             form = JSONUploadForm()

#         return render(request, "admin/upload_json.html", {"form": form})


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


# @admin.register(InventoryAsset)
# class InventoryAssetAdmin(admin.ModelAdmin):
#     """Admin for CSV-imported inventory assets"""

#     list_display = [
#         'asset_name', 'category', 'serial_number', 'assigned_person_name',
#         'assigned_email', 'status', 'claimed', 'pending_claim', 'mail_sent', 'created_at'
#     ]
#     list_filter = [
#         'category', 'status', 'claimed', 'pending_claim', 'mail_sent',
#         'assigned_user', 'created_at'
#     ]
#     search_fields = [
#         'asset_name', 'serial_number', 'assigned_person_name',
#         'assigned_email', 'assigned_user__email'
#     ]
#     readonly_fields = ['id', 'created_at', 'updated_at', 'mail_sent_at']

#     fieldsets = (
#         ('Asset Information', {
#             'fields': ('id', 'category', 'asset_name', 'serial_number', 'quantity', 'condition')
#         }),
#         ('Assignment', {
#             'fields': (
#                 'assigned_person_name', 'assigned_email', 'assigned_user',
#                 'assigned_date', 'assigned_by'
#             )
#         }),
#         ('Purchase', {
#             'fields': ('purchase_date',)
#         }),
#         ('Claim Status', {
#             'fields': ('claimed', 'pending_claim', 'status')
#         }),
#         ('Email Workflow', {
#             'fields': ('mail_sent', 'mail_sent_at')
#         }),
#         ('Acknowledgment', {
#             'fields': ('acknowledged', 'acknowledged_at')
#         }),
#         ('Additional Info', {
#             'fields': ('remarks', 'metadata')
#         }),
#         ('Timestamps', {
#             'fields': ('created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )

#     def get_queryset(self, request):
#         """Optimize queryset with select_related"""
#         return super().get_queryset(request).select_related('assigned_user')

#     actions = ['mark_claimed', 'mark_pending', 'send_claim_email']

#     def mark_claimed(self, request, queryset):
#         """Admin action: Mark as claimed"""
#         count = queryset.update(claimed=True, pending_claim=False, status='claimed')
#         self.message_user(request, f"{count} assets marked as claimed")
#     mark_claimed.short_description = "Mark selected as claimed"

#     def mark_pending(self, request, queryset):
#         """Admin action: Mark as pending claim"""
#         count = queryset.update(claimed=False, pending_claim=True, status='pending_claim')
#         self.message_user(request, f"{count} assets marked as pending")
#     mark_pending.short_description = "Mark selected as pending claim"

#     def send_claim_email(self, request, queryset):
#         """Admin action: Send claim emails to selected assets"""
#         from .email_service import email_service

#         sent_count = 0
#         failed_count = 0

#         for asset in queryset:
#             if not asset.assigned_email:
#                 failed_count += 1
#                 continue

#             result = email_service.send_inventory_claim_email(asset)
#             if result.get('success'):
#                 sent_count += 1
#             else:
#                 failed_count += 1

#         self.message_user(
#             request,
#             f"Emails sent: {sent_count}, Failed: {failed_count}"
#         )
#     send_claim_email.short_description = "Send claim emails to selected assets"


from django.contrib import admin, messages
from django import forms
from django.shortcuts import render, redirect
from django.urls import path
import json

from .models import Device, Assignment, TicketRequest, InventoryAsset

# =====================================================
# JSON Upload Form
# =====================================================


class JSONUploadForm(forms.Form):
    json_file = forms.FileField()


# =====================================================
# DEVICE ADMIN
# =====================================================


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):

    list_display = [
        "device_id",
        "device_type",
        "brand",
        "model",
        "status",
    ]

    list_filter = [
        "device_type",
        "brand",
        "status",
    ]

    search_fields = [
        "device_id",
        "brand",
        "model",
    ]

    change_list_template = "admin/device_changelist.html"

    def get_urls(self):

        urls = super().get_urls()

        custom_urls = [
            path(
                "upload-json/",
                self.upload_json,
                name="upload-json",
            ),
        ]

        return custom_urls + urls

    def upload_json(self, request):

        if request.method == "POST":

            form = JSONUploadForm(request.POST, request.FILES)

            if form.is_valid():

                file = request.FILES["json_file"]

                try:
                    data = json.load(file)

                except Exception:

                    self.message_user(
                        request, "Invalid JSON file", level=messages.ERROR
                    )

                    return redirect("..")

                inventory = data.get("inventory", {})

                created_count = 0

                mapping = {
                    "laptops": "laptop",
                    "mouse": "mouse",
                    "keyboards": "keyboard",
                    "pc_setups": "pc",
                    "headphones": "headphone",
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

                        name = (f"{brand} {model}").strip()

                        if not name:
                            name = device_type

                        specs = {
                            k: v
                            for k, v in item.items()
                            if k
                            not in [
                                "id",
                                "brand",
                                "model",
                            ]
                        }

                        Device.objects.create(
                            device_id=device_id,
                            name=name,
                            device_type=device_type,
                            brand=brand,
                            model=model,
                            specifications=specs,
                            status="available",
                            created_by=request.user,
                        )

                        created_count += 1

                self.message_user(
                    request,
                    f"{created_count} devices uploaded successfully",
                    level=messages.SUCCESS,
                )

                return redirect("..")

        else:

            form = JSONUploadForm()

        return render(request, "admin/upload_json.html", {"form": form})


# =====================================================
# ASSIGNMENT ADMIN
# =====================================================


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):

    list_display = [
        "device",
        "employee",
        "assigned_date",
        "status",
    ]

    list_filter = [
        "status",
        "assigned_date",
    ]

    search_fields = [
        "device__device_id",
        "employee__email",
    ]


# =====================================================
# TICKET REQUEST ADMIN
# =====================================================


@admin.register(TicketRequest)
class TicketRequestAdmin(admin.ModelAdmin):

    list_display = [
        "ticket_number",
        "requested_by",
        "ticket_type",
        "priority",
        "status",
    ]

    list_filter = [
        "ticket_type",
        "priority",
        "status",
    ]

    search_fields = [
        "ticket_number",
        "subject",
    ]


# =====================================================
# INVENTORY ASSET ADMIN
# =====================================================


@admin.register(InventoryAsset)
class InventoryAssetAdmin(admin.ModelAdmin):
    """
    Admin for CSV-imported inventory assets
    """

    # -------------------------------------------------
    # TABLE DISPLAY
    # -------------------------------------------------

    list_display = [
        "id",
        "asset_name",
        "category",
        "serial_number",
        "assigned_person_name",
        "desk_number",
        "assigned_email",
        "status",
        "claimed",
        "pending_claim",
        "mail_sent",
        "created_at",
    ]

    # -------------------------------------------------
    # FILTERS
    # -------------------------------------------------

    list_filter = [
        "category",
        "status",
        "claimed",
        "pending_claim",
        "mail_sent",
        "created_at",
    ]

    # -------------------------------------------------
    # SEARCH
    # -------------------------------------------------

    search_fields = [
        "asset_name",
        "serial_number",
        "assigned_person_name",
        "assigned_email",
        "desk_number",
    ]

    # -------------------------------------------------
    # SORTING
    # -------------------------------------------------

    ordering = ["-id"]

    # -------------------------------------------------
    # READONLY
    # -------------------------------------------------

    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
        "mail_sent_at",
    ]

    # -------------------------------------------------
    # FIELDSETS
    # -------------------------------------------------

    fieldsets = [
        (
            "Asset Information",
            {
                "fields": (
                    "id",
                    "category",
                    "asset_name",
                    "serial_number",
                    "quantity",
                    "condition",
                )
            },
        ),
        (
            "Assignment",
            {
                "fields": (
                    "assigned_person_name",
                    "desk_number",
                    "assigned_email",
                    "assigned_user",
                    "assigned_date",
                    "assigned_by",
                )
            },
        ),
        (
            "Purchase",
            {"fields": ("purchase_date",)},
        ),
        (
            "Claim Status",
            {
                "fields": (
                    "claimed",
                    "pending_claim",
                    "status",
                )
            },
        ),
        (
            "Email Workflow",
            {
                "fields": (
                    "mail_sent",
                    "mail_sent_at",
                )
            },
        ),
        (
            "Acknowledgment",
            {
                "fields": (
                    "acknowledged",
                    "acknowledged_at",
                )
            },
        ),
        (
            "Additional Info",
            {
                "fields": (
                    "remarks",
                    "metadata",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    ]

    # -------------------------------------------------
    # QUERY OPTIMIZATION
    # -------------------------------------------------

    def get_queryset(self, request):

        return super().get_queryset(request).select_related("assigned_user")

    # -------------------------------------------------
    # ACTIONS
    # -------------------------------------------------

    actions = [
        "mark_claimed",
        "mark_pending",
        "send_claim_email",
    ]

    # -------------------------------------------------
    # ACTION: MARK CLAIMED
    # -------------------------------------------------

    def mark_claimed(self, request, queryset):

        count = queryset.update(
            claimed=True,
            pending_claim=False,
            status="claimed",
        )

        self.message_user(request, f"{count} assets marked as claimed")

    mark_claimed.short_description = "Mark selected as claimed"

    # -------------------------------------------------
    # ACTION: MARK PENDING
    # -------------------------------------------------

    def mark_pending(self, request, queryset):

        count = queryset.update(
            claimed=False,
            pending_claim=True,
            status="pending_claim",
        )

        self.message_user(request, f"{count} assets marked as pending")

    mark_pending.short_description = "Mark selected as pending claim"

    # -------------------------------------------------
    # ACTION: SEND EMAILS
    # -------------------------------------------------

    def send_claim_email(self, request, queryset):

        from .email_service import email_service

        sent_count = 0
        failed_count = 0

        for asset in queryset:

            if not asset.assigned_email:

                failed_count += 1
                continue

            if asset.requires_desk_number_for_claim() and not asset.has_required_desk_number():

                failed_count += 1
                continue

            result = email_service.send_inventory_claim_email(asset)

            if result.get("success"):

                sent_count += 1

            else:

                failed_count += 1

        self.message_user(
            request, (f"Emails sent: " f"{sent_count}, " f"Failed: {failed_count}")
        )

    send_claim_email.short_description = "Send claim emails to selected assets"
