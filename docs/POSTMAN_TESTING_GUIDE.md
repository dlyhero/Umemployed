# Google Meet API Testing Guide for Postman

## Server Information
- **Base URL**: `http://127.0.0.1:8000`
- **API Base**: `http://127.0.0.1:8000/api/company/`

## Authentication
Most endpoints require authentication. You'll need to:
1. First login to get an access token
2. Add the token to the Authorization header: `Bearer YOUR_TOKEN`

## Google Meet API Endpoints to Test

### 1. Check Google Connection Status
- **Method**: GET
- **URL**: `http://127.0.0.1:8000/api/company/google/check-connection/`
- **Headers**: 
  ```
  Authorization: Bearer YOUR_TOKEN
  Content-Type: application/json
  ```
- **Expected Response**:
  ```json
  {
    "connected": false
  }
  ```

### 2. Initiate Google OAuth Connection
- **Method**: GET
- **URL**: `http://127.0.0.1:8000/api/company/google/connect/`
- **Headers**: 
  ```
  Authorization: Bearer YOUR_TOKEN
  Content-Type: application/json
  ```
- **Expected Response**:
  ```json
  {
    "authorization_url": "https://accounts.google.com/o/oauth2/auth?...",
    "state": "some_random_state"
  }
  ```

### 3. Create Google Meet Interview
- **Method**: POST
- **URL**: `http://127.0.0.1:8000/api/company/google/create-interview/`
- **Headers**: 
  ```
  Authorization: Bearer YOUR_TOKEN
  Content-Type: application/json
  ```
- **Body** (JSON):
  ```json
  {
    "candidate_id": 1,
    "job_title": "Software Engineer",
    "date": "2025-07-15",
    "time": "14:00",
    "timezone": "UTC",
    "note": "Technical interview for React developer position"
  }
  ```
- **Expected Response** (if not connected):
  ```json
  {
    "error": "Google Calendar not connected",
    "needs_google_auth": true
  }
  ```

### 4. List Interviews
- **Method**: GET
- **URL**: `http://127.0.0.1:8000/api/company/interviews/`
- **Headers**: 
  ```
  Authorization: Bearer YOUR_TOKEN
  Content-Type: application/json
  ```
- **Expected Response**:
  ```json
  [
    {
      "id": 1,
      "candidate_name": "John Doe",
      "date": "2025-07-15",
      "time": "14:00",
      "meeting_link": "https://meet.google.com/...",
      "note": "Technical interview"
    }
  ]
  ```

### 5. Disconnect Google Calendar
- **Method**: DELETE
- **URL**: `http://127.0.0.1:8000/api/company/google/disconnect/`
- **Headers**: 
  ```
  Authorization: Bearer YOUR_TOKEN
  Content-Type: application/json
  ```
- **Expected Response**:
  ```json
  {
    "success": true,
    "message": "Google Calendar disconnected successfully."
  }
  ```

## Step-by-Step Testing Process

### Step 1: Get Authentication Token
First, you need to authenticate to get a token. If you have existing authentication endpoints:

1. **Login Endpoint** (if available):
   - Method: POST
   - URL: `http://127.0.0.1:8000/api/auth/login/` (or similar)
   - Body: Your login credentials

### Step 2: Test Connection Status
1. Use the token from Step 1
2. Call the check connection endpoint
3. Should return `{"connected": false}` initially

### Step 3: Test OAuth Initiation
1. Call the Google connect endpoint
2. Should return an authorization URL
3. Note: You won't be able to complete the full OAuth flow in Postman, but you can verify the endpoint works

### Step 4: Test Interview Creation (Without Google)
1. Try creating an interview without Google connection
2. Should return an error asking to connect Google first

### Step 5: Test Other Endpoints
1. Test the list interviews endpoint
2. Test the disconnect endpoint

## Common Error Responses

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 400 Bad Request
```json
{
  "error": "Missing required fields"
}
```

### 500 Internal Server Error
```json
{
  "error": "Specific error message"
}
```

## Tips for Testing

1. **Save the environment**: Create a Postman environment with:
   - `base_url`: `http://127.0.0.1:8000`
   - `token`: Your authentication token

2. **Use variables**: In your requests, use `{{base_url}}` and `{{token}}`

3. **Check Django logs**: Watch the terminal where Django is running for any error messages

4. **Test incrementally**: Start with the check connection endpoint, then move to others

5. **Handle CSRF**: If you get CSRF errors, you might need to disable CSRF for API endpoints or include CSRF tokens

Let me know if you encounter any specific errors while testing these endpoints!
