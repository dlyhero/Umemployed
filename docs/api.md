# API Documentation

This document provides an overview of the Umemployed API endpoints.

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Most endpoints require an Authorization header with a Bearer token.

```
Authorization: Bearer <your_access_token>
```

### Authentication Endpoints

#### Sign Up

- **URL**: `/api/users/signup/`
- **Method**: `POST`
- **Auth required**: No
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "username": "username",
    "password": "secure_password",
    "confirm_password": "secure_password",
    "first_name": "First",
    "last_name": "Last"
  }
  ```
- **Success Response**: `201 Created`
  ```json
  {
    "message": "User created successfully. Please confirm your email."
  }
  ```

#### Login

- **URL**: `/api/users/login/`
- **Method**: `POST`
- **Auth required**: No
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "secure_password"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "email": "user@example.com",
    "role": "job_seeker",
    "user_id": 1,
    "access_token": "your_access_token",
    "refresh_token": "your_refresh_token",
    "has_resume": true
  }
  ```

## User Management

### Change Password

- **URL**: `/api/users/change-password/`
- **Method**: `POST`
- **Auth required**: Yes
- **Request Body**:
  ```json
  {
    "current_password": "current_password",
    "new_password": "new_password",
    "confirm_new_password": "new_password"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "message": "Password changed successfully. Please login again with your new password."
  }
  ```

### Delete Account

- **URL**: `/api/users/delete-account/`
- **Method**: `DELETE`
- **Auth required**: Yes
- **Success Response**: `204 No Content`

## Job Management

### List Jobs

- **URL**: `/api/jobs/`
- **Method**: `GET`
- **Auth required**: No
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `search`: Search term
  - `location`: Filter by location
  - `job_type`: Filter by job type
- **Success Response**: `200 OK`
  ```json
  {
    "count": 100,
    "next": "https://api.example.com/api/jobs/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "title": "Software Engineer",
        "company": "Tech Corp",
        "location": "New York, NY",
        "description": "Job description...",
        "salary_min": 80000,
        "salary_max": 120000,
        "created_at": "2023-01-01T00:00:00Z"
      },
      ...
    ]
  }
  ```

For more details, refer to the interactive API documentation at `/api/docs/` when the server is running.
