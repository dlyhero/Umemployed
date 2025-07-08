import logging

from django.contrib.auth import get_user_model
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

# Disable logging during tests to reduce noise
logging.disable(logging.CRITICAL)

User = get_user_model()


class DeleteAccountViewTest(TransactionTestCase):
    """Test the delete account functionality."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword123",
            first_name="Test",
            last_name="User",
        )
        self.url = reverse("delete-account")  # Adjust URL name as needed

    def test_delete_account_success(self):
        """Test successful account deletion."""
        # Authenticate the user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Store user ID for verification
        user_id = self.user.id

        # Make delete request
        response = self.client.delete(self.url)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn("message", response.data)
        self.assertIn("deleted_user_id", response.data)
        self.assertEqual(response.data["deleted_user_id"], user_id)

        # Verify user is actually deleted
        self.assertFalse(User.objects.filter(id=user_id).exists())

    def test_delete_account_unauthenticated(self):
        """Test that unauthenticated users cannot delete accounts."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Verify user still exists
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    def tearDown(self):
        # Re-enable logging after tests
        logging.disable(logging.NOTSET)
