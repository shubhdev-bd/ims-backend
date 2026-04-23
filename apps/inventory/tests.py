from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.models import Employee
from .models import Device, DeviceRequest


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
