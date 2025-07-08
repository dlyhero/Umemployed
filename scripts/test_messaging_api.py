#!/usr/bin/env python3
"""
Test script for messaging API endpoints
Run this to verify that all messaging views work correctly
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/home/nyuydine/Documents/UM/Umemployed')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umemployed.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from messaging.models import Conversation, ChatMessage, MessageReaction

User = get_user_model()

class MessagingAPITest:
    def __init__(self):
        self.client = APIClient()
        self.setup_test_data()
    
    def setup_test_data(self):
        """Create test users"""
        # Clean up existing test users
        User.objects.filter(username__in=['testuser1', 'testuser2']).delete()
        
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2', 
            email='test2@example.com',
            password='testpass123'
        )
        print("✓ Test users created")
    
    def test_conversation_flow(self):
        """Test complete conversation flow"""
        print("\n🧪 Testing Conversation Flow...")
        
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)
        
        # 1. Start conversation
        response = self.client.post('/api/messages/conversations/start/', {
            'user_id': self.user2.id
        })
        assert response.status_code == 201, f"Start conversation failed: {response.data}"
        conversation_id = response.data['conversation_id']
        print(f"✓ Conversation started (ID: {conversation_id})")
        
        # 2. Send message
        response = self.client.post(f'/api/messages/conversations/{conversation_id}/messages/', {
            'text': 'Hello, this is a test message!'
        })
        assert response.status_code == 201, f"Send message failed: {response.data}"
        print("✓ Message sent successfully")
        
        # 3. Get messages
        response = self.client.get(f'/api/messages/conversations/{conversation_id}/messages/')
        assert response.status_code == 200, f"Get messages failed: {response.data}"
        assert len(response.data) == 1, "Should have 1 message"
        message_id = response.data[0]['id']
        print("✓ Messages retrieved successfully")
        
        # 4. Add reaction
        response = self.client.post(f'/api/messages/messages/{message_id}/reactions/', {
            'reaction': 'like'
        })
        assert response.status_code == 201, f"Add reaction failed: {response.data}"
        print("✓ Reaction added successfully")
        
        # 5. Get conversations list
        response = self.client.get('/api/messages/conversations/')
        assert response.status_code == 200, f"Get conversations failed: {response.data}"
        assert len(response.data) >= 1, "Should have at least 1 conversation"
        print("✓ Conversations list retrieved")
        
        return conversation_id, message_id
    
    def test_message_operations(self, conversation_id, message_id):
        """Test message update and delete operations"""
        print("\n🧪 Testing Message Operations...")
        
        # Update message
        response = self.client.put(f'/api/messages/messages/{message_id}/update/', {
            'text': 'Updated message text'
        })
        assert response.status_code == 200, f"Update message failed: {response.data}"
        print("✓ Message updated successfully")
        
        # Mark messages as read (switch to user2)
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'/api/messages/conversations/{conversation_id}/mark-read/')
        assert response.status_code == 200, f"Mark as read failed: {response.data}"
        print("✓ Messages marked as read")
        
        # Search inbox
        response = self.client.get('/api/messages/search-inbox/?query=testuser1')
        assert response.status_code == 200, f"Search inbox failed: {response.data}"
        print("✓ Inbox search completed")
    
    def test_error_cases(self):
        """Test error handling"""
        print("\n🧪 Testing Error Cases...")
        
        # Test unauthorized access
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/messages/conversations/')
        assert response.status_code == 401, "Should require authentication"
        print("✓ Authentication required correctly")
        
        # Test invalid user ID for starting conversation
        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/api/messages/conversations/start/', {
            'user_id': 99999
        })
        assert response.status_code == 404, "Should return 404 for invalid user"
        print("✓ Invalid user ID handled correctly")
        
        # Test self-conversation
        response = self.client.post('/api/messages/conversations/start/', {
            'user_id': self.user1.id
        })
        assert response.status_code == 400, "Should prevent self-conversation"
        print("✓ Self-conversation prevented")
    
    def test_validation(self):
        """Test input validation"""
        print("\n🧪 Testing Input Validation...")
        
        self.client.force_authenticate(user=self.user1)
        
        # Test empty message
        conversation = Conversation.objects.create(
            participant1=self.user1, 
            participant2=self.user2
        )
        response = self.client.post(f'/api/messages/conversations/{conversation.id}/messages/', {
            'text': '   '  # Only whitespace
        })
        assert response.status_code == 400, "Should reject empty/whitespace messages"
        print("✓ Empty message validation works")
        
        # Test invalid reaction
        message = ChatMessage.objects.create(
            conversation=conversation,
            sender=self.user1,
            text="Test message"
        )
        response = self.client.post(f'/api/messages/messages/{message.id}/reactions/', {
            'reaction': 'invalid_reaction'
        })
        assert response.status_code == 400, "Should reject invalid reactions"
        print("✓ Invalid reaction validation works")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Messaging API Tests...\n")
        
        try:
            # Test main conversation flow
            conversation_id, message_id = self.test_conversation_flow()
            
            # Test message operations
            self.test_message_operations(conversation_id, message_id)
            
            # Test error cases
            self.test_error_cases()
            
            # Test validation
            self.test_validation()
            
            print("\n✅ All messaging API tests passed!")
            return True
            
        except AssertionError as e:
            print(f"\n❌ Test failed: {e}")
            return False
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            return False

if __name__ == '__main__':
    test = MessagingAPITest()
    success = test.run_all_tests()
    sys.exit(0 if success else 1)
