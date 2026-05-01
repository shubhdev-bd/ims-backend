from datetime import date

from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.models import Employee
from .models import Assignment, Device, DeviceRequest, TicketRequest


@override_settings(APPS_SCRIPT_URL="")
class DeviceGrantTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = Employee.objects.create_user(
            email="admin@example.com",
            password="StrongPass123!",
            first_name="Admin",
            last_name="User",
            role="admin",
            is_staff=True,
            email_verified=True,
        )
        self.employee = Employee.objects.create_user(
            email="employee@example.com",
            password="StrongPass123!",
            first_name="Regular",
            last_name="Employee",
            role="employee",
            email_verified=True,
        )
        self.device = Device.objects.create(
            device_id="DEV001",
            name="Dell Latitude",
            device_type="laptop",
            brand="Dell",
            model="Latitude 5430",
            serial_number="SN-12345",
            status="available",
            condition="good",
            created_by=self.admin,
        )
        self.device_request = DeviceRequest.objects.create(
            requested_by=self.employee,
            device_type="laptop",
            brand="Dell",
            model="Latitude",
            reason="Need a work laptop",
        )
        self.client.force_authenticate(user=self.admin)

    def test_grant_endpoint_creates_assignment_and_links_request(self):
        response = self.client.post(
            f"/api/inventory/device-requests/{self.device_request.id}/grant/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.device_request.refresh_from_db()
        self.device.refresh_from_db()

        self.assertEqual(self.device_request.status, "approved")
        self.assertIsNotNone(self.device_request.assignment)
        self.assertEqual(self.device_request.assignment.employee, self.employee)
        self.assertEqual(self.device_request.assignment.device, self.device)
        self.assertEqual(self.device_request.assignment.status, "approved")
        self.assertEqual(self.device.status, "assigned")

    def test_device_request_list_includes_assignment_details_after_grant(self):
        self.client.post(
            f"/api/inventory/device-requests/{self.device_request.id}/grant/",
            {},
            format="json",
        )

        response = self.client.get("/api/inventory/device-requests/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data[0] if isinstance(response.data, list) else response.data["results"][0]
        self.assertIn("assignment_details", data)
        self.assertEqual(data["assignment_details"]["device_details"]["device_id"], "DEV001")


@override_settings(APPS_SCRIPT_URL="")
class TicketWorkflowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = Employee.objects.create_user(
            email="admin-ticket@example.com",
            password="StrongPass123!",
            first_name="Admin",
            last_name="Ticket",
            role="admin",
            is_staff=True,
            email_verified=True,
        )
        self.employee = Employee.objects.create_user(
            email="employee-ticket@example.com",
            password="StrongPass123!",
            first_name="Ticket",
            last_name="Owner",
            role="employee",
            email_verified=True,
        )
        self.device = Device.objects.create(
            device_id="DEV002",
            name="Sony Laptop",
            device_type="laptop",
            brand="Sony",
            model="Vaio",
            serial_number="SN-67890",
            status="assigned",
            condition="good",
            created_by=self.admin,
        )

    def test_my_tickets_returns_full_ticket_and_normalized_status(self):
        TicketRequest.objects.create(
            requested_by=self.employee,
            ticket_type="issue",
            priority="medium",
            status="in_progress",
            device=self.device,
            subject="damage",
            description="Screen is cracked and needs service.",
        )

        self.client.force_authenticate(user=self.employee)
        response = self.client.get("/api/inventory/tickets/my_tickets/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data[0]
        self.assertEqual(data["status"], "approved")
        self.assertEqual(data["subject"], "damage")
        self.assertEqual(data["device_details"]["brand"], "Sony")
        self.assertEqual(data["description"], "Screen is cracked and needs service.")

    def test_ticket_status_patch_supports_new_ticket_workflow(self):
        ticket = TicketRequest.objects.create(
            requested_by=self.employee,
            ticket_type="repair",
            priority="medium",
            status="pending",
            device=self.device,
            subject="Keyboard issue",
            description="Some keys are no longer working properly.",
        )

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            f"/api/inventory/tickets/{ticket.id}/",
            {"status": "approved"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, "approved")

        response = self.client.patch(
            f"/api/inventory/tickets/{ticket.id}/",
            {"status": "on_repair"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, "on_repair")

        response = self.client.patch(
            f"/api/inventory/tickets/{ticket.id}/",
            {"status": "repaired"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, "repaired")
        self.assertIsNotNone(ticket.resolved_at)


@override_settings(APPS_SCRIPT_URL="")
class MyAssignmentsPayloadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = Employee.objects.create_user(
            email="admin-assignment@example.com",
            password="StrongPass123!",
            first_name="Admin",
            last_name="Assignment",
            role="admin",
            is_staff=True,
            email_verified=True,
        )
        self.employee = Employee.objects.create_user(
            email="employee-assignment@example.com",
            password="StrongPass123!",
            first_name="Assigned",
            last_name="User",
            role="employee",
            email_verified=True,
        )
        self.device = Device.objects.create(
            device_id="DEV003",
            name="MacBook Pro",
            device_type="laptop",
            brand="Apple",
            model='M3 Pro 14"',
            serial_number="SN-24680",
            status="assigned",
            condition="excellent",
            specifications={"ram": "18 GB", "storage": "512 GB"},
            location="HQ",
            notes="Issued with charger and sleeve",
            image_url="https://example.com/device.png",
            created_by=self.admin,
        )
        self.assignment = Assignment.objects.create(
            device=self.device,
            employee=self.employee,
            assigned_by=self.admin,
            status="active",
            expected_return_date=date(2026, 5, 10),
            consent_form_data={
                "employee_name": "Assigned User",
                "employee_id": self.employee.employee_id,
                "device_name": "MacBook Pro",
                "device_id": "DEV003",
                "received_date": "2026-05-01",
                "condition": "excellent",
                "accessories": "Charger, sleeve",
            },
            consent_images=["https://example.com/consent-1.png"],
        )

    def test_my_assignments_returns_full_assignment_device_and_consent_data(self):
        self.client.force_authenticate(user=self.employee)

        response = self.client.get("/api/inventory/assignments/my_assignments/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data[0]
        self.assertEqual(data["id"], str(self.assignment.id))
        self.assertEqual(data["device_details"]["device_id"], "DEV003")
        self.assertEqual(data["device_details"]["serial_number"], "SN-24680")
        self.assertEqual(data["device_details"]["image_url"], "https://example.com/device.png")
        self.assertEqual(data["expected_return_date"], "2026-05-10")
        self.assertEqual(data["consent_form_data"]["employee_name"], "Assigned User")
        self.assertEqual(data["consent_images"], ["https://example.com/consent-1.png"])
