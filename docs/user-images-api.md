# User Images API Guide

## Overview
This document provides the API endpoints for managing user's profile and cover images. Both images are optional and can be uploaded, retrieved, or deleted.

## Base URL
```
/api/resume/
```

## Authentication
All endpoints require authentication (Bearer token).

---

## 1. Get User's Current Images

**Endpoint:** `GET /api/resume/user-images/`

**Description:** Get the current user's profile and cover image URLs.

**Response:**
```json
{
  "images": {
    "profile_image": "/media/resume/images/profile_123.jpg",
    "cover_image": "/media/resume/covers/cover_123.jpg"
  }
}
```

**Example Request:**
```javascript
const response = await fetch('/api/resume/user-images/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const imageData = await response.json();
```

---

## 2. Upload Profile Image

**Endpoint:** `POST /api/resume/user-images/`

**Description:** Upload a profile image for the user.

**Request Body (Form-Data):**
```
Content-Type: multipart/form-data
profile_image: [image file]
```

**Response:**
```json
{
  "message": "Profile image uploaded successfully",
  "profile_image": "/media/resume/images/profile_123.jpg"
}
```

**Example Request:**
```javascript
const formData = new FormData();
formData.append('profile_image', imageFile);

const response = await fetch('/api/resume/user-images/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});
const result = await response.json();
```

---

## 3. Upload Cover Image

**Endpoint:** `POST /api/resume/user-images/`

**Description:** Upload a cover image for the user.

**Request Body (Form-Data):**
```
Content-Type: multipart/form-data
cover_image: [image file]
```

**Response:**
```json
{
  "message": "Cover image uploaded successfully",
  "cover_image": "/media/resume/covers/cover_123.jpg"
}
```

**Example Request:**
```javascript
const formData = new FormData();
formData.append('cover_image', imageFile);

const response = await fetch('/api/resume/user-images/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});
const result = await response.json();
```

---

## 4. Delete Profile Image

**Endpoint:** `DELETE /api/resume/user-images/?type=profile_image`

**Description:** Delete the user's profile image.

**Response:**
```json
{
  "message": "Profile image deleted successfully"
}
```

**Example Request:**
```javascript
const response = await fetch('/api/resume/user-images/?type=profile_image', {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const result = await response.json();
```

---

## 5. Delete Cover Image

**Endpoint:** `DELETE /api/resume/user-images/?type=cover_image`

**Description:** Delete the user's cover image.

**Response:**
```json
{
  "message": "Cover image deleted successfully"
}
```

**Example Request:**
```javascript
const response = await fetch('/api/resume/user-images/?type=cover_image', {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const result = await response.json();
```

---

## Complete Frontend Implementation Example

```javascript
class UserImagesService {
  constructor(token) {
    this.token = token;
    this.baseUrl = '/api/resume/';
  }

  // Get current images
  async getCurrentImages() {
    const response = await fetch(`${this.baseUrl}user-images/`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    return await response.json();
  }

  // Upload profile image
  async uploadProfileImage(imageFile) {
    const formData = new FormData();
    formData.append('profile_image', imageFile);

    const response = await fetch(`${this.baseUrl}user-images/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`
      },
      body: formData
    });
    return await response.json();
  }

  // Upload cover image
  async uploadCoverImage(imageFile) {
    const formData = new FormData();
    formData.append('cover_image', imageFile);

    const response = await fetch(`${this.baseUrl}user-images/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`
      },
      body: formData
    });
    return await response.json();
  }

  // Delete profile image
  async deleteProfileImage() {
    const response = await fetch(`${this.baseUrl}user-images/?type=profile_image`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });
    return await response.json();
  }

  // Delete cover image
  async deleteCoverImage() {
    const response = await fetch(`${this.baseUrl}user-images/?type=cover_image`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });
    return await response.json();
  }
}

// Usage example
const userImagesService = new UserImagesService(userToken);

// Load current images
async function loadUserImages() {
  try {
    const imageData = await userImagesService.getCurrentImages();
    displayImages(imageData.images);
  } catch (error) {
    console.error('Error loading images:', error);
  }
}

// Upload profile image
async function uploadProfileImage(file) {
  try {
    const result = await userImagesService.uploadProfileImage(file);
    console.log('Profile image uploaded:', result.profile_image);
    // Update UI with new image
    updateProfileImage(result.profile_image);
  } catch (error) {
    console.error('Error uploading profile image:', error);
  }
}

// Upload cover image
async function uploadCoverImage(file) {
  try {
    const result = await userImagesService.uploadCoverImage(file);
    console.log('Cover image uploaded:', result.cover_image);
    // Update UI with new image
    updateCoverImage(result.cover_image);
  } catch (error) {
    console.error('Error uploading cover image:', error);
  }
}

// Delete profile image
async function deleteProfileImage() {
  try {
    const result = await userImagesService.deleteProfileImage();
    console.log('Profile image deleted:', result.message);
    // Update UI to remove image
    removeProfileImage();
  } catch (error) {
    console.error('Error deleting profile image:', error);
  }
}

// Delete cover image
async function deleteCoverImage() {
  try {
    const result = await userImagesService.deleteCoverImage();
    console.log('Cover image deleted:', result.message);
    // Update UI to remove image
    removeCoverImage();
  } catch (error) {
    console.error('Error deleting cover image:', error);
  }
}
```

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid data (e.g., non-image file)
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: Image not found (for delete operations)
- `500 Internal Server Error`: Server error

Error responses follow this format:
```json
{
  "error": "Error message description"
}
```

---

## Notes

1. **File Types**: Only image files are accepted (JPEG, PNG, GIF, etc.)

2. **File Size**: Consider implementing file size limits on the frontend

3. **Image Storage**: Images are stored in the media directory:
   - Profile images: `resume/images/`
   - Cover images: `resume/covers/`

4. **Optional Images**: Both profile and cover images are optional

5. **Image URLs**: Returned URLs are relative to your domain (e.g., `/media/resume/images/profile.jpg`)

6. **Default Profile Image**: If no profile image is uploaded, a default image is used

7. **Image Replacement**: Uploading a new image automatically replaces the existing one

8. **File Cleanup**: When deleting images, the files are automatically removed from storage 