from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Employee


class EmployeeUsernameTests(TestCase):
    def test_username_is_generated_from_name(self):
        employee = Employee.objects.create_user(
            email="john.doe@example.com",
            password="StrongPass123!",
            first_name="John",
            last_name="Doe",
        )

        self.assertEqual(employee.username, "john.doe")

    def test_duplicate_names_get_unique_usernames(self):
        first_employee = Employee.objects.create_user(
            email="alex.one@example.com",
            password="StrongPass123!",
            first_name="Alex",
            last_name="Smith",
        )
        second_employee = Employee.objects.create_user(
            email="alex.two@example.com",
            password="StrongPass123!",
            first_name="Alex",
            last_name="Smith",
        )

        self.assertEqual(first_employee.username, "alex.smith")
        self.assertEqual(second_employee.username, "alex.smith1")


class LoginIdentifierTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.employee = Employee.objects.create_user(
            email="jane.doe@example.com",
            password="StrongPass123!",
            first_name="Jane",
            last_name="Doe",
            email_verified=True,
        )

    def test_login_with_email_still_works(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": self.employee.email, "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["employee"]["username"], self.employee.username)
        self.assertTrue(response.data["employee"]["email_verified"])

    def test_login_with_username_works(self):
        response = self.client.post(
            "/api/auth/login/",
            {"login": self.employee.username, "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["employee"]["email"], self.employee.email)
        self.assertIn("tokens", response.data)

    def test_admin_login_rejects_non_admin_accounts(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "login": self.employee.username,
                "password": "StrongPass123!",
                "admin_only": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This login page is for admin accounts only.", str(response.data))
