# Edit Profile Page - Backend API Guide

## Overview
This document provides all the API endpoints required for the Edit Profile page functionality, including dropdowns for job titles, countries, states, and resume management.

## Base URL
```
/api/resume/
```

## Authentication
All endpoints require authentication (Bearer token) except for dropdown endpoints.

---

## 1. Job Titles Dropdown

**Endpoint:** `GET /api/resume/skill-categories/`

**Description:** Get all available job titles/skill categories for dropdown selection.

**Response:**
```json
[
  {"id": 1, "name": "Web Designer"},
  {"id": 2, "name": "Web Developer"}, 
  {"id": 3, "name": "UI / UX Designer"},
  {"id": 4, "name": "Software Engineer"},
  {"id": 5, "name": "Product Manager"},
  {"id": 6, "name": "Data Scientist"},
  {"id": 7, "name": "DevOps Engineer"}
]
```

**Example Request:**
```javascript
const response = await fetch('/api/resume/skill-categories/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const jobTitles = await response.json();
```

---

## 2. Countries Dropdown

**Endpoint:** `GET /api/resume/countries/`

**Description:** Get all available countries for dropdown selection.

**Response:**
```json
{
  "countries": [
    {"code": "US", "name": "United States"},
    {"code": "CA", "name": "Canada"},
    {"code": "UK", "name": "United Kingdom"},
    {"code": "AU", "name": "Australia"},
    {"code": "DE", "name": "Germany"},
    {"code": "FR", "name": "France"}
  ]
}
```

**Example Request:**
```javascript
const response = await fetch('/api/resume/countries/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const data = await response.json();
const countries = data.countries;
```

---

## 3. States/Locations Dropdown

**Endpoint:** `GET /api/resume/states/`

**Description:** Get all US states for dropdown selection with "Not in US" option at the top for international users.

**Response:**
```json
{
  "states": [
    {"code": "NOT_US", "name": "Not in US"},
    {"code": "NY", "name": "New York"},
    {"code": "CA", "name": "California"},
    {"code": "TX", "name": "Texas"},
    {"code": "FL", "name": "Florida"},
    {"code": "NC", "name": "North Carolina"},
    {"code": "SC", "name": "South Carolina"}
  ]
}
```

**Example Request:**
```javascript
const response = await fetch('/api/resume/states/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const data = await response.json();
const states = data.states;
```

**Note:** The "Not in US" option is always at the top of the list for international users. When selected, it will clear the state field in the database.

---

## 4. Get Current Resume Details

**Endpoint:** `GET /api/resume/resume-details/`

**Description:** Get the current user's resume information.

**Response:**
```json
{
  "id": 1,
  "user": 1,
  "first_name": "John",
  "surname": "Doe", 
  "job_title": "Software Engineer",
  "description": "Experienced developer with expertise in backend development...",
  "phone": "+1234567890",
  "state": "NY",
  "country": "United States",
  "date_of_birth": "1990-12-25",
  "category": 1,
  "skills": [
    {
      "id": 1,
      "name": "JavaScript"
    },
    {
      "id": 2,
      "name": "Python"
    }
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Example Request:**
```javascript
const response = await fetch('/api/resume/resume-details/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const resumeData = await response.json();
```

---

## 5. Update Resume Details

**Endpoint:** `PATCH /api/resume/update-resume-fields/`

**Description:** Update specific fields of the user's resume.

**Request Body:**
```json
{
  "first_name": "John",
  "surname": "Doe", 
  "job_title": "Software Engineer",
  "description": "Experienced developer with expertise in backend development...",
  "phone": "+1234567890",
  "address": "123 Main Street",
  "city": "New York",
  "state": "NY",
  "country": "United States"
}
```

**Response:** Returns the updated resume data (same structure as GET response).

**Example Request:**
```javascript
const response = await fetch('/api/resume/update-resume-fields/', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    first_name: "John",
    surname: "Doe",
    job_title: "Software Engineer",
    description: "Experienced developer...",
    phone: "+1234567890",
    address: "123 Main Street",
    city: "New York",
    state: "NY",
    country: "United States"
  })
});
const updatedResume = await response.json();
```

**State Field Handling:**
- Use `"NOT_US"` as the state value for international users (this will clear the state field)
- Use state codes like `"NY"`, `"CA"`, `"TX"` for US states
- The state information is saved to the database in the Resume model

---

## Complete Frontend Implementation Example

```javascript
class EditProfileService {
  constructor(token) {
    this.token = token;
    this.baseUrl = '/api/resume/';
  }

  // Get all dropdown data
  async getDropdownData() {
    try {
      const [jobTitles, countries, states] = await Promise.all([
        this.getJobTitles(),
        this.getCountries(),
        this.getStates()
      ]);

      return { jobTitles, countries, states };
    } catch (error) {
      console.error('Error fetching dropdown data:', error);
      throw error;
    }
  }

  // Get job titles
  async getJobTitles() {
    const response = await fetch(`${this.baseUrl}skill-categories/`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    return await response.json();
  }

  // Get countries
  async getCountries() {
    const response = await fetch(`${this.baseUrl}countries/`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    const data = await response.json();
    return data.countries;
  }

  // Get states
  async getStates() {
    const response = await fetch(`${this.baseUrl}states/`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    const data = await response.json();
    return data.states;
  }

  // Get current resume data
  async getResumeData() {
    const response = await fetch(`${this.baseUrl}resume-details/`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    return await response.json();
  }

  // Update resume data
  async updateResume(resumeData) {
    const response = await fetch(`${this.baseUrl}update-resume-fields/`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(resumeData)
    });
    return await response.json();
  }
}

// Usage example
const editProfileService = new EditProfileService(userToken);

// Load edit profile page
async function loadEditProfilePage() {
  try {
    // Get all dropdown data and current resume data
    const [dropdownData, resumeData] = await Promise.all([
      editProfileService.getDropdownData(),
      editProfileService.getResumeData()
    ]);

    // Populate dropdowns
    populateJobTitlesDropdown(dropdownData.jobTitles);
    populateCountriesDropdown(dropdownData.countries);
    populateStatesDropdown(dropdownData.states);

    // Populate form with current data
    populateFormWithResumeData(resumeData);

  } catch (error) {
    console.error('Error loading edit profile page:', error);
  }
}

// Save profile changes
async function saveProfileChanges(formData) {
  try {
    const updatedResume = await editProfileService.updateResume(formData);
    console.log('Profile updated successfully:', updatedResume);
    // Show success message to user
  } catch (error) {
    console.error('Error updating profile:', error);
    // Show error message to user
  }
}
```

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid data
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses follow this format:
```json
{
  "error": "Error message description"
}
```

---

## Notes

1. **Job Title Impact on Skills**: When a user updates their `job_title`, the Skills API (`/api/resume/skills/`) will automatically show relevant skills based on their job category.

2. **Partial Updates**: The PATCH endpoint supports partial updates - you can send only the fields you want to update.

3. **Validation**: The backend validates all input data and returns detailed error messages for invalid fields.

4. **Authentication**: All endpoints except dropdown endpoints require a valid Bearer token in the Authorization header. 