# Optimized Skills API Guide

## Overview
This document provides the optimized API endpoints for managing skills with improved performance, pagination, and filtering capabilities. The API is designed to handle large datasets efficiently.

## Performance Optimizations
- **Database-level pagination** (LIMIT/OFFSET) instead of loading all data
- **Efficient queries** with `select_related` and `prefetch_related`
- **Cached user skill IDs** to avoid N+1 queries
- **Search with database indexes** for faster lookups
- **Category filtering** at database level
- **Optimized sorting** with database-level operations

## Base URL
```
/api/resume/
```

## Authentication
All endpoints require authentication (Bearer token).

---

## 1. Get User's Skills (Optimized)

**Endpoint:** `GET /api/resume/skills/`

**Description:** Get user's skills with optimized pagination, search, and filtering.

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `page_size` | integer | 20 | Items per page (max: 100) |
| `search` | string | - | Search skills by name (case-insensitive) |
| `filter` | string | `job_relevant` | Filter type: `job_relevant`, `user_only`, `all`, `category:<id>` |
| `category` | integer | - | Filter by specific category ID |
| `sort` | string | `name` | Sort order: `name`, `popularity`, `relevance` |

### Filter Types

- **`job_relevant`** (default): User's skills + skills from their job category
- **`user_only`**: Only skills the user has
- **`all`**: All available skills
- **`category:<id>`**: Skills from specific category (e.g., `category:5`)

### Sort Options

- **`name`** (default): Alphabetical order
- **`popularity`**: By number of users who have the skill
- **`relevance`**: By relevance to user's job category

### Response
```json
{
  "count": 150,
  "next": "http://api.example.com/skills/?page=2",
  "previous": null,
  "results": {
    "skills": [
      {
        "id": 1,
        "name": "JavaScript",
        "is_user_skill": true,
        "categories": ["Frontend Development", "Web Development"]
      }
    ],
    "filter_applied": "job_relevant",
    "job_category": "Software Development",
    "search_term": "java",
    "total_user_skills": 15
  }
}
```

### Example Requests

**Basic request:**
```javascript
const response = await fetch('/api/resume/skills/', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

**With search and pagination:**
```javascript
const response = await fetch('/api/resume/skills/?search=python&page=2&page_size=10', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

**Filter by category:**
```javascript
const response = await fetch('/api/resume/skills/?filter=category:5&sort=popularity', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

---

## 2. Get Optimized Skill Categories

**Endpoint:** `GET /api/resume/skill-categories-optimized/`

**Description:** Get skill categories with usage statistics and user context.

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_stats` | boolean | `true` | Include skill and user counts |
| `user_only` | boolean | `false` | Show only categories user has skills in |

### Response
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Frontend Development",
      "skill_count": 25,
      "user_count": 150,
      "is_user_category": true
    }
  ],
  "total_categories": 20,
  "user_categories_count": 5,
  "user_job_category": {
    "id": 1,
    "name": "Software Development"
  }
}
```

### Example Request
```javascript
const response = await fetch('/api/resume/skill-categories-optimized/?include_stats=true&user_only=false', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

---

## 3. Add Skills to User Profile

**Endpoint:** `POST /api/resume/skills/`

**Description:** Add existing skill(s) to user's profile.

### Request Body

**Single skill:**
```json
{
  "skill_id": 15
}
```

**Multiple skills:**
```json
{
  "skill_ids": [15, 23, 45]
}
```

### Response
```json
{
  "message": "Successfully added 2 skill(s)",
  "skills_added": ["Python", "Django"],
  "skills_already_owned": ["JavaScript"],
  "total_user_skills": 18
}
```

### Example Request
```javascript
const response = await fetch('/api/resume/skills/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    skill_ids: [15, 23, 45]
  })
});
```

---

## 4. Remove Skills from User Profile

**Endpoint:** `DELETE /api/resume/skills/`

**Description:** Remove skill(s) from user's profile.

### Request Body

**Single skill:**
```json
{
  "skill_id": 15
}
```

**Multiple skills:**
```json
{
  "skill_ids": [15, 23, 45]
}
```

### Response
```json
{
  "message": "Successfully removed 2 skill(s)",
  "skills_removed": ["Python", "Django"],
  "skills_not_found": ["InvalidSkill"],
  "total_user_skills": 16
}
```

### Example Request
```javascript
const response = await fetch('/api/resume/skills/', {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    skill_ids: [15, 23]
  })
});
```

---

## Complete Frontend Implementation Example

```javascript
class OptimizedSkillsService {
  constructor(token) {
    this.token = token;
    this.baseUrl = '/api/resume/';
  }

  // Get user's skills with advanced filtering
  async getUserSkills(options = {}) {
    const {
      page = 1,
      pageSize = 20,
      search = '',
      filter = 'job_relevant',
      category = null,
      sort = 'name'
    } = options;

    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
      filter,
      sort
    });

    if (search) params.append('search', search);
    if (category) params.append('category', category.toString());

    const response = await fetch(`${this.baseUrl}skills/?${params}`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    return await response.json();
  }

  // Get optimized skill categories
  async getSkillCategories(options = {}) {
    const {
      includeStats = true,
      userOnly = false
    } = options;

    const params = new URLSearchParams({
      include_stats: includeStats.toString(),
      user_only: userOnly.toString()
    });

    const response = await fetch(`${this.baseUrl}skill-categories-optimized/?${params}`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    return await response.json();
  }

  // Add skills to user profile
  async addSkills(skillIds) {
    const payload = Array.isArray(skillIds) 
      ? { skill_ids: skillIds }
      : { skill_id: skillIds };

    const response = await fetch(`${this.baseUrl}skills/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });
    return await response.json();
  }

  // Remove skills from user profile
  async removeSkills(skillIds) {
    const payload = Array.isArray(skillIds) 
      ? { skill_ids: skillIds }
      : { skill_id: skillIds };

    const response = await fetch(`${this.baseUrl}skills/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });
    return await response.json();
  }
}

// Usage examples
const skillsService = new OptimizedSkillsService(userToken);

// Load skills with search and pagination
async function loadSkills(searchTerm = '', page = 1) {
  try {
    const result = await skillsService.getUserSkills({
      search: searchTerm,
      page: page,
      pageSize: 20,
      filter: 'job_relevant',
      sort: 'relevance'
    });
    
    displaySkills(result.results.skills);
    updatePagination(result);
  } catch (error) {
    console.error('Error loading skills:', error);
  }
}

// Load skill categories with statistics
async function loadSkillCategories() {
  try {
    const result = await skillsService.getSkillCategories({
      includeStats: true,
      userOnly: false
    });
    
    displayCategories(result.categories);
    highlightUserJobCategory(result.user_job_category);
  } catch (error) {
    console.error('Error loading categories:', error);
  }
}

// Add multiple skills
async function addSkillsToProfile(skillIds) {
  try {
    const result = await skillsService.addSkills(skillIds);
    console.log('Skills added:', result.skills_added);
    
    // Refresh skills list
    await loadSkills();
  } catch (error) {
    console.error('Error adding skills:', error);
  }
}

// Remove skills
async function removeSkillsFromProfile(skillIds) {
  try {
    const result = await skillsService.removeSkills(skillIds);
    console.log('Skills removed:', result.skills_removed);
    
    // Refresh skills list
    await loadSkills();
  } catch (error) {
    console.error('Error removing skills:', error);
  }
}

// Search skills with debouncing
let searchTimeout;
function searchSkills(searchTerm) {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    loadSkills(searchTerm, 1); // Reset to first page when searching
  }, 300); // 300ms debounce
}

// Filter by category
function filterByCategory(categoryId) {
  loadSkills('', 1, 'category:' + categoryId);
}
```

---

## Performance Tips

### Frontend Optimization

1. **Implement debouncing** for search inputs (300-500ms delay)
2. **Use pagination** instead of loading all skills at once
3. **Cache responses** for frequently accessed data
4. **Implement virtual scrolling** for large skill lists
5. **Use optimistic updates** for add/remove operations

### Backend Optimization

1. **Database indexes** on frequently searched fields
2. **Query optimization** with `select_related` and `prefetch_related`
3. **Caching** for static data like categories
4. **Connection pooling** for database connections
5. **Compression** for API responses

### Recommended Page Sizes

- **Mobile**: 10-15 items per page
- **Desktop**: 20-30 items per page
- **Search results**: 15-20 items per page

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid parameters
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

## Migration from Old API

If you're migrating from the old skills API:

1. **Update endpoint URLs** to use the new optimized endpoints
2. **Add pagination parameters** to handle large datasets
3. **Implement search functionality** for better UX
4. **Use category filtering** for more targeted results
5. **Update error handling** for new response formats

The new API is backward compatible for basic operations but provides significant performance improvements for large datasets. 