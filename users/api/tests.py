from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class ChooseAccountTypeTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="password123"
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/choose-account-type/"

    def test_choose_recruiter_account_type(self):
        response = self.client.post(self.url, {"account_type": "recruiter"}, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.is_recruiter)
        self.assertFalse(self.user.is_applicant)

    def test_choose_job_seeker_account_type(self):
        response = self.client.post(self.url, {"account_type": "job_seeker"}, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.is_applicant)
        self.assertFalse(self.user.is_recruiter)

    def test_invalid_account_type(self):
        response = self.client.post(self.url, {"account_type": "invalid_type"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
