# Simple Skills API Guide

## Overview
This is a simplified skills API focused on the two main use cases:
1. **job_relevant**: Skills suggestions based on user's job category
2. **user_only**: Skills the user has already saved

## Base URL
```
/api/resume/
```

## Authentication
All endpoints require authentication (Bearer token).

---

## Get Skills (Simple)

**Endpoint:** `GET /api/resume/skills-simple/`

**Description:** Get skills with simple filtering - no pagination, just the two main use cases.

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filter` | string | `job_relevant` | Filter type: `job_relevant` or `user_only` |
| `search` | string | - | Search skills by name (optional) |

### Filter Types

- **`job_relevant`** (default): Skills from user's job category + user's existing skills
- **`user_only`**: Only skills the user has already saved

### Response
```json
{
  "skills": [
    {
      "id": 1,
      "name": "JavaScript",
      "is_user_skill": true,
      "categories": ["Frontend Development"]
    },
    {
      "id": 2,
      "name": "Python",
      "is_user_skill": false,
      "categories": ["Backend Development"]
    }
  ],
  "filter_applied": "job_relevant",
  "job_category": "Software Development",
  "search_term": null,
  "total_count": 25,
  "user_skills_count": 5
}
```

### Example Requests

**Get job-relevant skills (default):**
```javascript
const response = await fetch('/api/resume/skills-simple/', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

**Get user's saved skills only:**
```javascript
const response = await fetch('/api/resume/skills-simple/?filter=user_only', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

**Search within job-relevant skills:**
```javascript
const response = await fetch('/api/resume/skills-simple/?search=python', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

---

## Frontend Implementation Example

```javascript
class SimpleSkillsService {
  constructor(token) {
    this.token = token;
    this.baseUrl = '/api/resume/';
  }

  // Get job-relevant skills (suggestions)
  async getJobRelevantSkills(searchTerm = '') {
    const params = new URLSearchParams({ filter: 'job_relevant' });
    if (searchTerm) params.append('search', searchTerm);

    const response = await fetch(`${this.baseUrl}skills-simple/?${params}`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    return await response.json();
  }

  // Get user's saved skills
  async getUserSkills(searchTerm = '') {
    const params = new URLSearchParams({ filter: 'user_only' });
    if (searchTerm) params.append('search', searchTerm);

    const response = await fetch(`${this.baseUrl}skills-simple/?${params}`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    return await response.json();
  }
}

// Usage examples
const skillsService = new SimpleSkillsService(userToken);

// Load job-relevant skills for suggestions
async function loadJobRelevantSkills(searchTerm = '') {
  try {
    const result = await skillsService.getJobRelevantSkills(searchTerm);
    console.log('Job relevant skills:', result.skills);
    console.log('User has', result.user_skills_count, 'skills');
    
    // Display skills with suggestions
    displaySkills(result.skills, result.filter_applied);
  } catch (error) {
    console.error('Error loading job-relevant skills:', error);
  }
}

// Load user's saved skills
async function loadUserSkills(searchTerm = '') {
  try {
    const result = await skillsService.getUserSkills(searchTerm);
    console.log('User skills:', result.skills);
    
    // Display user's skills
    displayUserSkills(result.skills);
  } catch (error) {
    console.error('Error loading user skills:', error);
  }
}

// Display skills with different styling for user vs suggested
function displaySkills(skills, filterType) {
  const container = document.getElementById('skills-container');
  container.innerHTML = '';
  
  skills.forEach(skill => {
    const skillElement = document.createElement('div');
    skillElement.className = `skill-item ${skill.is_user_skill ? 'user-skill' : 'suggested-skill'}`;
    
    skillElement.innerHTML = `
      <span class="skill-name">${skill.name}</span>
      ${skill.is_user_skill ? '<span class="badge">✓ Saved</span>' : '<span class="badge">+ Add</span>'}
      <span class="skill-categories">${skill.categories.join(', ')}</span>
    `;
    
    // Add click handler for suggested skills
    if (!skill.is_user_skill) {
      skillElement.addEventListener('click', () => addSkillToUser(skill.id));
    }
    
    container.appendChild(skillElement);
  });
}

// Add skill to user's profile
async function addSkillToUser(skillId) {
  try {
    const response = await fetch('/api/resume/skills/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${userToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ skill_id: skillId })
    });
    
    const result = await response.json();
    console.log('Skill added:', result);
    
    // Refresh the skills list
    await loadJobRelevantSkills();
  } catch (error) {
    console.error('Error adding skill:', error);
  }
}

// Search functionality with debouncing
let searchTimeout;
function searchSkills(searchTerm, filterType = 'job_relevant') {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    if (filterType === 'user_only') {
      loadUserSkills(searchTerm);
    } else {
      loadJobRelevantSkills(searchTerm);
    }
  }, 300);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  // Load job-relevant skills by default
  loadJobRelevantSkills();
  
  // Set up search input
  const searchInput = document.getElementById('skills-search');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      searchSkills(e.target.value);
    });
  }
  
  // Set up filter buttons
  const jobRelevantBtn = document.getElementById('filter-job-relevant');
  const userOnlyBtn = document.getElementById('filter-user-only');
  
  if (jobRelevantBtn) {
    jobRelevantBtn.addEventListener('click', () => {
      loadJobRelevantSkills();
      updateActiveFilter('job_relevant');
    });
  }
  
  if (userOnlyBtn) {
    userOnlyBtn.addEventListener('click', () => {
      loadUserSkills();
      updateActiveFilter('user_only');
    });
  }
});

function updateActiveFilter(filterType) {
  // Update UI to show active filter
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  document.getElementById(`filter-${filterType.replace('_', '-')}`).classList.add('active');
}
```

---

## CSS Styling Example

```css
.skill-item {
  display: flex;
  align-items: center;
  padding: 10px;
  margin: 5px 0;
  border: 1px solid #ddd;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.skill-item:hover {
  background-color: #f5f5f5;
}

.user-skill {
  background-color: #e8f5e8;
  border-color: #4caf50;
}

.suggested-skill {
  background-color: #fff3cd;
  border-color: #ffc107;
}

.skill-name {
  font-weight: bold;
  margin-right: 10px;
}

.badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  margin-right: 10px;
}

.user-skill .badge {
  background-color: #4caf50;
  color: white;
}

.suggested-skill .badge {
  background-color: #ffc107;
  color: #333;
}

.skill-categories {
  color: #666;
  font-size: 12px;
  margin-left: auto;
}

.filter-btn {
  padding: 8px 16px;
  margin: 0 5px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  border-radius: 4px;
}

.filter-btn.active {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}
```

---

## Key Benefits

1. **Simple and Fast**: No pagination, just the skills you need
2. **Two Clear Use Cases**: 
   - `job_relevant`: For skill suggestions
   - `user_only`: For showing saved skills
3. **Clear Indicators**: `is_user_skill` flag shows which skills are saved
4. **Search Support**: Optional search within each filter
5. **Context Information**: Shows job category and counts

This simplified API should work perfectly for your frontend needs! 