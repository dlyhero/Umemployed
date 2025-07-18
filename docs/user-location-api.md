# User Location API Guide

## Overview
This document provides the API endpoints for managing user's country and city information, including dropdowns for countries.

## Base URL
```
/api/resume/
```

## Authentication
All endpoints require authentication (Bearer token) except for the countries dropdown.

---

## 1. Countries Dropdown

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
    {"code": "FR", "name": "France"},
    {"code": "IN", "name": "India"},
    {"code": "CN", "name": "China"},
    {"code": "JP", "name": "Japan"},
    {"code": "BR", "name": "Brazil"}
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

## 2. Get User's Current Location

**Endpoint:** `GET /api/resume/user-location/`

**Description:** Get the current user's country and city information.

**Response:**
```json
{
  "location": {
    "country": "CA",
    "country_name": "Canada",
    "city": "Toronto"
  }
}
```

**Example Request:**
```javascript
const response = await fetch('/api/resume/user-location/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const locationData = await response.json();
```

---

## 3. Update User's Location

**Endpoint:** `POST /api/resume/user-location/` or `PATCH /api/resume/user-location/`

**Description:** Update the user's country and city information.

**Request Body:**
```json
{
  "country": "CA",
  "city": "Toronto"
}
```

**Response:** Returns the updated location data (same structure as GET response).

**Example Request:**
```javascript
const response = await fetch('/api/resume/user-location/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    country: "CA",
    city: "Toronto"
  })
});
const updatedLocation = await response.json();
```

---

## Complete Frontend Implementation Example

```javascript
class LocationService {
  constructor(token) {
    this.token = token;
    this.baseUrl = '/api/resume/';
  }

  // Get all countries for dropdown
  async getCountries() {
    const response = await fetch(`${this.baseUrl}countries/`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    const data = await response.json();
    return data.countries;
  }

  // Get user's current location
  async getCurrentLocation() {
    const response = await fetch(`${this.baseUrl}user-location/`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    return await response.json();
  }

  // Update user's location
  async updateLocation(countryCode, city) {
    const response = await fetch(`${this.baseUrl}user-location/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        country: countryCode,
        city: city
      })
    });
    return await response.json();
  }
}

// Usage example
const locationService = new LocationService(userToken);

// Load location page
async function loadLocationPage() {
  try {
    // Get countries dropdown and current location
    const [countries, currentLocation] = await Promise.all([
      locationService.getCountries(),
      locationService.getCurrentLocation()
    ]);

    // Populate countries dropdown
    populateCountriesDropdown(countries);

    // Populate form with current location
    populateFormWithLocation(currentLocation.location);

  } catch (error) {
    console.error('Error loading location page:', error);
  }
}

// Save location changes
async function saveLocationChanges(countryCode, city) {
  try {
    const updatedLocation = await locationService.updateLocation(countryCode, city);
    console.log('Location updated successfully:', updatedLocation);
    // Show success message to user
  } catch (error) {
    console.error('Error updating location:', error);
    // Show error message to user
  }
}
```

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid data (e.g., invalid country code)
- `401 Unauthorized`: Missing or invalid token
- `500 Internal Server Error`: Server error

Error responses follow this format:
```json
{
  "error": "Error message description"
}
```

---

## Notes

1. **Country Codes**: Use ISO 3166-1 alpha-2 country codes (e.g., "US", "CA", "UK")

2. **International Support**: This API is designed for international users, not just US users

3. **Data Consistency**: The API updates both ContactInfo and Resume models to maintain data consistency

4. **Validation**: Country codes are validated against the django-countries library

5. **Default Values**: If no location is set, empty strings are returned for country and city 