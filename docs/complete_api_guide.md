# Complete UmEmployed API Documentation & Testing Guide

## Overview
This comprehensive guide covers all API endpoints for the UmEmployed platform, including Job Management and Messaging features. It provides Postman testing instructions and frontend development guidance.

---

## 🔐 Authentication

All API endpoints require authentication using JWT tokens (except public endpoints).

### Headers Required:
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

### Base URLs:
- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

---

## 📋 Job Management API

### Base URL: `/api/jobs/`

### 1. Job Creation Flow (With AI Processing)

#### Step 1: Create Basic Job Details
**Endpoint**: `POST /api/jobs/create-step1/`
**Purpose**: Creates a new job with basic information and validates recruiter subscription

```json
{
  "title": "Senior Python Developer",
  "hire_number": 3,
  "job_location_type": "remote",
  "job_type": "Full_time",
  "location": "US",
  "salary_range": "100001-150000",
  "category": 1
}
```

**Response**: Returns job ID and basic details
**Notes**: 
- Requires active recruiter subscription
- Consumes posting quota
- Returns 403 if quota exceeded

#### Step 2: Add Job Preferences
**Endpoint**: `PATCH /api/jobs/{job_id}/create-step2/`

```json
{
  "job_type": "Full_time",
  "experience_levels": "3-5Years",
  "weekly_ranges": "mondayToFriday",
  "shifts": "dayShift"
}
```

#### Step 3: Add Description (AI Skill Extraction)
**Endpoint**: `PATCH /api/jobs/{job_id}/create-step3/`

```json
{
  "description": "We are seeking an experienced Python developer with Django expertise...",
  "responsibilities": "Lead development of web applications, mentor junior developers...",
  "benefits": "Competitive salary, health insurance, remote work flexibility..."
}
```

**AI Feature**: Automatically extracts technical skills from job description

#### Step 4: Finalize Job (AI Question Generation)
**Endpoint**: `PATCH /api/jobs/{job_id}/create-step4/`

```json
{
  "requirements": [1, 5, 8, 12],
  "level": "Mid"
}
```

**AI Features**: 
- Generates assessment questions for each skill
- Sets job as available/published
- Sends notifications

### 2. Job Update Flow (No AI Processing - Fast Updates)

#### Update Basic Details
**Endpoint**: `PATCH /api/jobs/{job_id}/update-step1/`

```json
{
  "title": "Senior Python Developer (Remote)",
  "salary_range": "150001+"
}
```

#### Update Preferences
**Endpoint**: `PATCH /api/jobs/{job_id}/update-step2/`

```json
{
  "experience_levels": "5-10Years",
  "shifts": "flexibleShift"
}
```

#### Update Description (No AI)
**Endpoint**: `PATCH /api/jobs/{job_id}/update-step3/`

```json
{
  "description": "Updated job description...",
  "benefits": "Enhanced benefits package..."
}
```

**Note**: Does NOT extract skills or call ChatGPT

#### Update Requirements (No AI)
**Endpoint**: `PATCH /api/jobs/{job_id}/update-step4/`

```json
{
  "requirements": [1, 5, 8],
  "level": "Expert"
}
```

**Note**: Does NOT generate new questions

### 3. Job Management Endpoints

#### Toggle Job Availability
**Endpoint**: `PATCH /api/jobs/{job_id}/toggle-availability/`

```json
{
  "is_available": false
}
```

#### List Recruiter's Jobs
**Endpoint**: `GET /api/jobs/my-jobs/`
**Response**: List of all jobs created by the authenticated recruiter

#### Get Job Details
**Endpoint**: `GET /api/jobs/my-jobs/{job_id}/`
**Response**: Detailed job information

#### Get Job Options (Dropdowns)
**Endpoint**: `GET /api/jobs/job-options/`
**Response**: Categories, salary ranges, locations, etc.

#### Get Extracted Skills
**Endpoint**: `GET /api/jobs/{job_id}/extracted-skills/`
**Response**: List of AI-extracted skills for the job

### 4. Public Job Endpoints

#### List All Jobs
**Endpoint**: `GET /api/jobs/jobs/`
**Purpose**: Public job listings

#### Job Details
**Endpoint**: `GET /api/jobs/jobs/{job_id}/`
**Purpose**: Public job details

#### Search Jobs
**Endpoint**: `GET /api/jobs/jobs/search/`
**Query Parameters**:
- `keyword`: Search term
- `location`: Country code
- `salary_range`: Salary range
- `job_type`: Job type
- `category`: Category ID

### 5. Job Application Endpoints

#### Apply for Job
**Endpoint**: `POST /api/jobs/jobs/{job_id}/apply/`

#### Save Job
**Endpoint**: `POST /api/jobs/jobs/{job_id}/save/`

#### Withdraw Application
**Endpoint**: `DELETE /api/jobs/jobs/{job_id}/withdraw/`

#### Get Job Questions
**Endpoint**: `GET /api/jobs/{job_id}/questions/`
**Purpose**: Fetch assessment questions for a job

#### Submit Answers
**Endpoint**: `POST /api/jobs/{job_id}/questions/`

```json
{
  "responses": [
    {
      "question_id": 1,
      "answer": "A",
      "skill_id": 5
    }
  ]
}
```

#### List Applied Jobs
**Endpoint**: `GET /api/jobs/applied-jobs/`

#### List Saved Jobs
**Endpoint**: `GET /api/jobs/saved-jobs/`

---

## 💬 Messaging API

### Base URL: `/api/messages/`

### 1. Conversation Management

#### List All Conversations
**Endpoint**: `GET /api/messages/conversations/`
**Response**: All conversations for the authenticated user

```json
[
  {
    "id": 1,
    "participant1": 1,
    "participant2": 2,
    "participant1_username": "john_doe",
    "participant2_username": "jane_smith",
    "created_at": "2025-07-09T12:00:00Z"
  }
]
```

#### Start New Conversation
**Endpoint**: `POST /api/messages/conversations/start/`

```json
{
  "user_id": 2
}
```

**Response**:
```json
{
  "conversation_id": 1
}
```

#### Delete Conversation
**Endpoint**: `DELETE /api/messages/conversations/{conversation_id}/delete/`

#### Search Conversations
**Endpoint**: `GET /api/messages/search-inbox/?query=john`
**Purpose**: Search conversations by participant name

### 2. Message Management

#### Get Messages in Conversation
**Endpoint**: `GET /api/messages/conversations/{conversation_id}/messages/`

**Response**:
```json
[
  {
    "id": 1,
    "conversation": 1,
    "sender": 1,
    "sender_username": "john_doe",
    "text": "Hello!",
    "timestamp": "2025-07-09T12:00:00Z",
    "is_read": false,
    "reactions": [
      {
        "id": 1,
        "user": 2,
        "username": "jane_smith",
        "reaction": "like"
      }
    ]
  }
]
```

#### Send Message
**Endpoint**: `POST /api/messages/conversations/{conversation_id}/messages/`

```json
{
  "text": "Hello! How are you?"
}
```

**Response**:
```json
{
  "id": 2,
  "conversation": 1,
  "sender": 1,
  "sender_username": "john_doe",
  "text": "Hello! How are you?",
  "timestamp": "2025-07-09T12:05:00Z",
  "is_read": false,
  "reactions": []
}
```

#### Update Message
**Endpoint**: `PUT /api/messages/messages/{message_id}/update/`

```json
{
  "text": "Updated message text"
}
```

#### Delete Message
**Endpoint**: `DELETE /api/messages/messages/{message_id}/delete/`

#### Bulk Delete Messages
**Endpoint**: `POST /api/messages/conversations/{conversation_id}/bulk-delete/`

```json
{
  "message_ids": [1, 2, 3]
}
```

#### Mark Messages as Read
**Endpoint**: `POST /api/messages/conversations/{conversation_id}/mark-read/`

### 3. Message Reactions

#### Add Reaction
**Endpoint**: `POST /api/messages/messages/{message_id}/reactions/`

```json
{
  "reaction": "like"
}
```

**Available Reactions**: like, love, laugh, wow, sad, angry

#### Remove Reaction
**Endpoint**: `DELETE /api/messages/messages/{message_id}/reactions/`

```json
{
  "reaction": "like"
}
```

---

## 🧪 Postman Testing Collection

### Collection Setup

1. **Create New Collection**: "UmEmployed API"
2. **Set Variables**:
   - `baseUrl`: `http://localhost:8000`
   - `token`: `<your_jwt_token>`

### Environment Variables
```json
{
  "baseUrl": "http://localhost:8000",
  "token": "your_jwt_token_here",
  "jobId": "1",
  "conversationId": "1",
  "messageId": "1"
}
```

### Pre-request Script (for authenticated endpoints)
```javascript
pm.request.headers.add({
    key: 'Authorization',
    value: 'Bearer ' + pm.environment.get('token')
});
```

### Test Examples

#### Job Creation Test
```javascript
// Test for create-step1
pm.test("Job creation successful", function () {
    pm.response.to.have.status(201);
    const response = pm.response.json();
    pm.expect(response).to.have.property('id');
    pm.environment.set('jobId', response.id);
});
```

#### Messaging Test
```javascript
// Test for starting conversation
pm.test("Conversation started", function () {
    pm.response.to.have.status(201);
    const response = pm.response.json();
    pm.expect(response).to.have.property('conversation_id');
    pm.environment.set('conversationId', response.conversation_id);
});
```

---

## 🎨 Frontend Development Guide

### State Management Structure

```typescript
// Redux Store Structure
interface AppState {
  auth: {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
  };
  jobs: {
    myJobs: Job[];
    appliedJobs: Application[];
    savedJobs: Job[];
    currentJob: Job | null;
    loading: boolean;
  };
  messaging: {
    conversations: Conversation[];
    currentConversation: Conversation | null;
    messages: Message[];
    loading: boolean;
  };
}
```

### API Service Layer

```typescript
// api/jobService.ts
class JobService {
  private baseURL = '/api/jobs';

  // Job Creation Flow
  async createJobStep1(data: CreateJobStep1Data): Promise<Job> {
    return this.post(`${this.baseURL}/create-step1/`, data);
  }

  async updateJobStep1(jobId: number, data: Partial<CreateJobStep1Data>): Promise<Job> {
    return this.patch(`${this.baseURL}/${jobId}/update-step1/`, data);
  }

  // Job Management
  async getMyJobs(): Promise<Job[]> {
    return this.get(`${this.baseURL}/my-jobs/`);
  }

  async toggleJobAvailability(jobId: number, isAvailable: boolean): Promise<void> {
    return this.patch(`${this.baseURL}/${jobId}/toggle-availability/`, { is_available: isAvailable });
  }
}

// api/messagingService.ts
class MessagingService {
  private baseURL = '/api/messages';

  async getConversations(): Promise<Conversation[]> {
    return this.get(`${this.baseURL}/conversations/`);
  }

  async sendMessage(conversationId: number, text: string): Promise<void> {
    return this.post(`${this.baseURL}/conversations/${conversationId}/messages/`, { text });
  }

  async startConversation(userId: number): Promise<{ conversation_id: number }> {
    return this.post(`${this.baseURL}/conversations/start/`, { user_id: userId });
  }
}
```

### Component Examples

#### Job Management Component
```typescript
// components/JobManagement.tsx
import React, { useEffect, useState } from 'react';
import { JobService } from '../api/jobService';

const JobManagement: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const jobService = new JobService();

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      const myJobs = await jobService.getMyJobs();
      setJobs(myJobs);
    } catch (error) {
      console.error('Failed to load jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleJobStatus = async (jobId: number, currentStatus: boolean) => {
    try {
      await jobService.toggleJobAvailability(jobId, !currentStatus);
      loadJobs(); // Refresh list
    } catch (error) {
      console.error('Failed to update job status:', error);
    }
  };

  return (
    <div className="job-management">
      <h2>My Jobs</h2>
      {loading ? (
        <div>Loading...</div>
      ) : (
        <div className="job-list">
          {jobs.map(job => (
            <div key={job.id} className="job-card">
              <h3>{job.title}</h3>
              <p>Status: {job.is_available ? 'Published' : 'Draft'}</p>
              <button 
                onClick={() => toggleJobStatus(job.id, job.is_available)}
                className={job.is_available ? 'btn-secondary' : 'btn-primary'}
              >
                {job.is_available ? 'Unpublish' : 'Publish'}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
```

#### Messaging Component
```typescript
// components/Messaging.tsx
import React, { useEffect, useState } from 'react';
import { MessagingService } from '../api/messagingService';

const Messaging: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const messagingService = new MessagingService();

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    const convos = await messagingService.getConversations();
    setConversations(convos);
  };

  const loadMessages = async (conversationId: number) => {
    const msgs = await messagingService.getMessages(conversationId);
    setMessages(msgs);
    setCurrentConversation(conversationId);
  };

  const sendMessage = async () => {
    if (!currentConversation || !newMessage.trim()) return;
    
    await messagingService.sendMessage(currentConversation, newMessage);
    setNewMessage('');
    loadMessages(currentConversation); // Refresh messages
  };

  return (
    <div className="messaging-container">
      <div className="conversations-list">
        {conversations.map(conv => (
          <div key={conv.id} onClick={() => loadMessages(conv.id)}>
            {conv.participant1} - {conv.participant2}
          </div>
        ))}
      </div>
      
      <div className="chat-area">
        <div className="messages">
          {messages.map(msg => (
            <div key={msg.id} className="message">
              <strong>{msg.sender}:</strong> {msg.text}
            </div>
          ))}
        </div>
        
        <div className="message-input">
          <input
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type a message..."
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          />
          <button onClick={sendMessage}>Send</button>
        </div>
      </div>
    </div>
  );
};
```

### Real-time Updates (WebSocket)

```typescript
// hooks/useWebSocket.ts
import { useEffect, useState } from 'react';

export const useWebSocket = (url: string) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [lastMessage, setLastMessage] = useState<any>(null);

  useEffect(() => {
    const ws = new WebSocket(url);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLastMessage(data);
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, [url]);

  const sendMessage = (message: any) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message));
    }
  };

  return { lastMessage, sendMessage };
};
```

### Error Handling

```typescript
// utils/apiClient.ts
class ApiClient {
  async request(url: string, options: RequestInit = {}) {
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getToken()}`,
          ...options.headers,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new ApiError(response.status, errorData.message || 'Request failed');
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new ApiError(500, 'Network error');
    }
  }
}

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}
```

---

## 🚀 Key Implementation Points for Frontend

### 1. Job Management Features
- **Job Creation Wizard**: 4-step process with validation
- **Quick Edit Mode**: Fast updates without AI processing
- **Job Status Toggle**: Instant publish/unpublish
- **Real-time Updates**: Job application notifications

### 2. Messaging Features
- **Real-time Chat**: WebSocket for instant messaging
- **Conversation Management**: List, search, delete conversations
- **Message Actions**: Edit, delete, react to messages
- **Unread Indicators**: Mark messages as read functionality

### 3. Performance Considerations
- **Lazy Loading**: Load conversations and messages on demand
- **Caching**: Cache job lists and conversation data
- **Optimistic Updates**: Update UI immediately, sync with server
- **Error Recovery**: Retry failed requests, show offline status

### 4. User Experience
- **Loading States**: Show spinners during API calls
- **Error Messages**: Clear feedback on failures
- **Success Notifications**: Confirm successful actions
- **Responsive Design**: Mobile-friendly interface

This comprehensive guide provides everything needed for both testing the APIs with Postman and implementing the frontend features. The separation between job creation (with AI) and job updates (without AI) ensures optimal performance for routine editing tasks.
