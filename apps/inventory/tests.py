from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.models import Employee
from .models import Device, DeviceRequest, TicketRequest


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
