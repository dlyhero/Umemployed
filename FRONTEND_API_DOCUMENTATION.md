# Resume API Endpoints - Frontend Integration Guide

This documentation provides comprehensive information for integrating the Resume API endpoints into your Next.js frontend application.

## Base URL
```
https://your-domain.com/api/resume/
```

## Authentication
All endpoints (except countries) require authentication. Include the authorization header:
```javascript
headers: {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
}
```

---

## 1. Countries API

### Endpoint: `GET /api/resume/countries/`
**Purpose:** Get list of all countries for dropdown selections  
**Authentication:** Not required

### What This Endpoint Does
This endpoint retrieves a static list of all available countries from the backend database. It's designed to populate dropdown menus and select components in forms where users need to choose their country of residence or nationality.

### Backend Logic
- Fetches all country records from the database
- Returns countries with both country code (ISO format) and display name
- No user authentication required since this is reference data
- Data is returned in alphabetical order by country name
- Cached for performance since country data rarely changes

### Endpoint Logic
This endpoint fetches all countries from the Django database and returns them in a simplified format for use in frontend dropdowns. The endpoint:
- Queries the `Country` model to get all available countries
- Maps each country to include only the essential fields (code and name)
- Returns the data in a consistent format that's optimized for frontend consumption
- Does not require authentication as country data is public information
- Uses caching internally to improve performance for frequently accessed data

### Response Structure
```json
{
  "countries": [
    {
      "code": "US",
      "name": "United States"
    },
    {
      "code": "CA", 
      "name": "Canada"
    },
    {
      "code": "GB",
      "name": "United Kingdom"
    }
  ]
}
```

### Next.js Implementation
```javascript
// hooks/useCountries.js
import { useState, useEffect } from 'react';

export const useCountries = () => {
  const [countries, setCountries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCountries = async () => {
      try {
        const response = await fetch('/api/resume/countries/');
        const data = await response.json();
        setCountries(data.countries);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchCountries();
  }, []);

  return { countries, loading, error };
};

// components/CountrySelect.jsx
import { useCountries } from '../hooks/useCountries';

const CountrySelect = ({ value, onChange }) => {
  const { countries, loading, error } = useCountries();

  if (loading) return <div>Loading countries...</div>;
  if (error) return <div>Error loading countries</div>;

  return (
    <select value={value} onChange={(e) => onChange(e.target.value)}>
      <option value="">Select a country</option>
      {countries.map((country) => (
        <option key={country.code} value={country.name}>
          {country.name}
        </option>
      ))}
    </select>
  );
};
```

---

## 2. About API

### Endpoint: `GET|PUT|PATCH /api/resume/about/`
**Purpose:** Manage user's about/bio information  
**Authentication:** Required

### What This Endpoint Does
This endpoint manages the user's personal summary or "about me" section of their resume. This section typically contains a brief professional overview, career objectives, or personal statement that introduces the candidate to potential employers.

### Backend Logic
- **GET**: Fetches the authenticated user's about section including name and bio from their profile
- **PUT/PATCH**: Updates the user's about section with new content (firstName, lastName, bio)
- Requires user authentication to ensure data privacy and ownership
- Returns empty/null fields if user hasn't filled out sections yet
- Validates input length and content format before saving
- Part of the user's complete resume profile data structure
- Automatically tracks last updated timestamp for version control

### GET Response Structure
```json
{
  "about": {
    "firstName": "John",
    "lastName": "Doe", 
    "bio": "Experienced software engineer with 5+ years...",
    "description": "Passionate about creating innovative solutions..."
  }
}
```

### PUT/PATCH Request Structure
```json
{
  "about": {
    "firstName": "John",           // Optional - User's first name
    "lastName": "Doe",             // Optional - User's last name  
    "bio": "New bio text...",      // Optional - Short bio/summary
    "description": "Detailed..."   // Optional - Longer description
  }
}
```

### Next.js Implementation
```javascript
// hooks/useAbout.js
import { useState, useEffect } from 'react';

export const useAbout = () => {
  const [about, setAbout] = useState({
    firstName: '',
    lastName: '',
    bio: '',
    description: ''
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAbout = async () => {
    try {
      const response = await fetch('/api/resume/about/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        }
      });
      const data = await response.json();
      setAbout(data.about);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateAbout = async (aboutData) => {
    try {
      setLoading(true);
      const response = await fetch('/api/resume/about/', {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ about: aboutData })
      });
      
      if (!response.ok) throw new Error('Failed to update about');
      
      const data = await response.json();
      setAbout(data.about);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAbout();
  }, []);

  return { about, loading, error, updateAbout, refetch: fetchAbout };
};

// components/AboutForm.jsx
import { useState } from 'react';
import { useAbout } from '../hooks/useAbout';

const AboutForm = () => {
  const { about, loading, error, updateAbout } = useAbout();
  const [formData, setFormData] = useState(about);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await updateAbout(formData);
      alert('About information updated successfully!');
    } catch (error) {
      alert('Failed to update about information');
    }
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  if (loading) return <div>Loading...</div>;

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="First Name"
        value={formData.firstName}
        onChange={(e) => handleChange('firstName', e.target.value)}
      />
      <input
        type="text"
        placeholder="Last Name"
        value={formData.lastName}
        onChange={(e) => handleChange('lastName', e.target.value)}
      />
      <textarea
        placeholder="Bio"
        value={formData.bio}
        onChange={(e) => handleChange('bio', e.target.value)}
      />
      <textarea
        placeholder="Description"
        value={formData.description}
        onChange={(e) => handleChange('description', e.target.value)}
      />
      <button type="submit">Update About</button>
    </form>
  );
};
```

---

## 3. Personal Details API

### Endpoint: `GET|PUT|PATCH /api/resume/personal-details/`
**Purpose:** Manage user's personal details and contact information  
**Authentication:** Required

### What This Endpoint Does
This endpoint manages the user's personal contact information and details that are essential for their resume. This includes contact information, location data, and personal identifiers that employers need to reach out to candidates.

### Backend Logic
- **GET**: Fetches the authenticated user's personal details from their profile
- **PUT/PATCH**: Updates the user's personal details with new information
- Handles date formatting (converts database dates to readable format like "25th Dec, 1990")
- Manages location data including address, city, country relationships
- Validates email format, phone number format, and postal codes
- Ensures data consistency between related fields (city/country)
- Returns formatted data optimized for display in resume templates
- Automatically handles timezone considerations for date fields

### GET Response Structure
```json
{
  "personalDetails": {
    "email": "john.doe@example.com",
    "dob": "25th Dec, 1990",           // Formatted date of birth
    "address": "123 Main Street",      // Street address
    "city": "New York",                // City name
    "country": "United States",        // Country name
    "postalCode": "10001",            // Postal/ZIP code (not stored yet)
    "mobile": "+1-234-567-8900",      // Phone number
    "jobTitle": "Software Engineer"    // Current job title
  }
}
```

### Next.js Implementation
```javascript
// hooks/usePersonalDetails.js
import { useState, useEffect } from 'react';

export const usePersonalDetails = () => {
  const [personalDetails, setPersonalDetails] = useState({
    email: '',
    dob: '',
    address: '',
    city: '',
    country: '',
    postalCode: '',
    mobile: '',
    jobTitle: ''
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchPersonalDetails = async () => {
    try {
      const response = await fetch('/api/resume/personal-details/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        }
      });
      const data = await response.json();
      setPersonalDetails(data.personalDetails);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updatePersonalDetails = async (detailsData) => {
    try {
      setLoading(true);
      const response = await fetch('/api/resume/personal-details/', {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ personalDetails: detailsData })
      });
      
      if (!response.ok) throw new Error('Failed to update personal details');
      
      const data = await response.json();
      setPersonalDetails(data.personalDetails);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPersonalDetails();
  }, []);

  return { personalDetails, loading, error, updatePersonalDetails, refetch: fetchPersonalDetails };
};
```

---

## 4. Experiences API

### Endpoint: `GET|POST /api/resume/experiences/`
**Purpose:** Manage user's work experiences  
**Authentication:** Required

### GET Response Structure
```json
{
  "experiences": [
    {
      "id": 1,
      "period": "2019-22",                           // Calculated from dates
      "logo": "/assets/shree-logo-Bd9DHJ8p.png",    // Default company logo
      "title": "Full Stack Developer",               // Job title/role
      "company": "Shreethemes - India",             // Company name
      "description": "Led development of web applications..."
    },
    {
      "id": 2,
      "period": "2017-19",
      "logo": "/assets/circle-logo-De1zeqcD.png", 
      "title": "Back-end Developer",
      "company": "CircleCI - U.S.A.",
      "description": "Worked as Back-end Developer at CircleCI"
    }
  ]
}
```

### POST Request Structure
```json
{
  "title": "Senior Software Engineer",      // Required - Job title
  "company": "Google Inc.",                 // Required - Company name
  "period": "2020-23",                     // Optional - Format: "YYYY-YY" or "YYYY-Present"
  "description": "Led development team..." // Optional - Job description
}
```

### Next.js Implementation
```javascript
// hooks/useExperiences.js
import { useState, useEffect } from 'react';

export const useExperiences = () => {
  const [experiences, setExperiences] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchExperiences = async () => {
    try {
      const response = await fetch('/api/resume/experiences/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        }
      });
      const data = await response.json();
      setExperiences(data.experiences);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const addExperience = async (experienceData) => {
    try {
      setLoading(true);
      const response = await fetch('/api/resume/experiences/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(experienceData)
      });
      
      if (!response.ok) throw new Error('Failed to add experience');
      
      const data = await response.json();
      setExperiences(data.experiences);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExperiences();
  }, []);

  return { experiences, loading, error, addExperience, refetch: fetchExperiences };
};

// components/ExperienceForm.jsx
import { useState } from 'react';
import { useExperiences } from '../hooks/useExperiences';

const ExperienceForm = () => {
  const { addExperience } = useExperiences();
  const [formData, setFormData] = useState({
    title: '',
    company: '',
    period: '',
    description: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await addExperience(formData);
      setFormData({ title: '', company: '', period: '', description: '' });
      alert('Experience added successfully!');
    } catch (error) {
      alert('Failed to add experience');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Job Title"
        value={formData.title}
        onChange={(e) => setFormData({...formData, title: e.target.value})}
        required
      />
      <input
        type="text"
        placeholder="Company Name"
        value={formData.company}
        onChange={(e) => setFormData({...formData, company: e.target.value})}
        required
      />
      <input
        type="text"
        placeholder="Period (e.g., 2020-23)"
        value={formData.period}
        onChange={(e) => setFormData({...formData, period: e.target.value})}
      />
      <textarea
        placeholder="Job Description"
        value={formData.description}
        onChange={(e) => setFormData({...formData, description: e.target.value})}
      />
      <button type="submit">Add Experience</button>
    </form>
  );
};
```

---

## 5. Education API

### Endpoint: `GET|POST /api/resume/education/`
**Purpose:** Manage user's education records  
**Authentication:** Required

### GET Response Structure
```json
{
  "education": [
    {
      "id": 1,
      "period": "2013-17",                               // Calculated from graduation year
      "degree": "Bachelor of Computer Science",          // Degree name
      "university": "University of London",              // Institution name
      "description": "Specialized in web development and software engineering..."
    },
    {
      "id": 2,
      "period": "2011-13",
      "degree": "High School Diploma",
      "university": "London Tech High School", 
      "description": "Focus on mathematics and computer science fundamentals..."
    }
  ]
}
```

### POST Request Structure
```json
{
  "degree": "Master of Science in Computer Science",    // Required - Degree name
  "university": "Stanford University",                  // Required - Institution name
  "period": "2020-22",                                 // Optional - Format: "YYYY-YY"
  "description": "Specialized in machine learning..."   // Optional - Field of study/description
}
```

### Next.js Implementation
```javascript
// hooks/useEducation.js
import { useState, useEffect } from 'react';

export const useEducation = () => {
  const [education, setEducation] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchEducation = async () => {
    try {
      const response = await fetch('/api/resume/education/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        }
      });
      const data = await response.json();
      setEducation(data.education);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const addEducation = async (educationData) => {
    try {
      setLoading(true);
      const response = await fetch('/api/resume/education/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(educationData)
      });
      
      if (!response.ok) throw new Error('Failed to add education');
      
      const data = await response.json();
      setEducation(data.education);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEducation();
  }, []);

  return { education, loading, error, addEducation, refetch: fetchEducation };
};
```

---

## 6. Skills API

### Endpoint: `GET|POST /api/resume/skills/`
**Purpose:** Manage user's skills with pagination, search, and job title filtering  
**Authentication:** Required

### GET Response Structure (Paginated)
```json
{
  "count": 50,                                    // Total number of skills
  "next": "http://localhost:8000/api/resume/skills/?page=2",  // Next page URL
  "previous": null,                               // Previous page URL  
  "results": {
    "skills": [
      {
        "id": 1,
        "name": "JavaScript",
        "is_user_skill": true,              // User already has this skill
        "categories": ["Frontend Development"]
      },
      {
        "id": 2,
        "name": "React",
        "is_user_skill": false,             // Suggested skill based on job title
        "categories": ["Frontend Development"]
      }
    ],
    "filter_applied": "job_relevant",           // Which filter was applied
    "job_category": "Frontend Development"      // User's job category (if found)
  }
}
```

### Query Parameters
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)
- `search`: Search skills by name (case-insensitive)
- `filter`: Filter type (default: 'job_relevant')
  - `job_relevant`: User's skills + skills relevant to their job title
  - `user_only`: Only user's existing skills
  - `all`: All available skills in the system

### POST Request Structure
```json
{
  "name": "Node.js"                              // Required - Skill name
}
```

### Next.js Implementation
```javascript
// hooks/useSkills.js
import { useState, useEffect } from 'react';

export const useSkills = () => {
  const [skills, setSkills] = useState([]);
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSkills = async (params = {}) => {
    try {
      setLoading(true);
      const queryParams = new URLSearchParams({
        page: 1,
        page_size: 20,
        filter: 'job_relevant',
        ...params
      });

      const response = await fetch(`/api/resume/skills/?${queryParams}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        }
      });
      
      const data = await response.json();
      setSkills(data.results.skills);
      setPagination({
        count: data.count,
        next: data.next,
        previous: data.previous
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const addSkill = async (skillName) => {
    try {
      const response = await fetch('/api/resume/skills/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: skillName })
      });
      
      if (!response.ok) throw new Error('Failed to add skill');
      
      const data = await response.json();
      setSkills(data.results.skills);
      setPagination({
        count: data.count,
        next: data.next,
        previous: data.previous
      });
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const searchSkills = async (searchTerm) => {
    await fetchSkills({ search: searchTerm, page: 1 });
  };

  const filterSkills = async (filterType) => {
    await fetchSkills({ filter: filterType, page: 1 });
  };

  const loadPage = async (pageNum) => {
    await fetchSkills({ page: pageNum });
  };

  useEffect(() => {
    fetchSkills();
  }, []);

  return { 
    skills, 
    pagination, 
    loading, 
    error, 
    addSkill, 
    searchSkills, 
    filterSkills, 
    loadPage,
    refetch: fetchSkills 
  };
};

// components/SkillsManager.jsx
import { useState } from 'react';
import { useSkills } from '../hooks/useSkills';

const SkillsManager = () => {
  const { 
    skills, 
    pagination, 
    loading, 
    addSkill, 
    searchSkills, 
    filterSkills, 
    loadPage 
  } = useSkills();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState('job_relevant');
  const [newSkill, setNewSkill] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    searchSkills(searchTerm);
  };

  const handleFilterChange = (newFilter) => {
    setFilter(newFilter);
    filterSkills(newFilter);
  };

  const handleAddSkill = async (e) => {
    e.preventDefault();
    if (!newSkill.trim()) return;
    
    try {
      await addSkill(newSkill);
      setNewSkill('');
      alert('Skill added successfully!');
    } catch (error) {
      alert('Failed to add skill');
    }
  };

  if (loading) return <div>Loading skills...</div>;

  return (
    <div>
      {/* Search */}
      <form onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Search skills..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <button type="submit">Search</button>
      </form>

      {/* Filter */}
      <div>
        <button 
          onClick={() => handleFilterChange('job_relevant')}
          className={filter === 'job_relevant' ? 'active' : ''}
        >
          Job Relevant
        </button>
        <button 
          onClick={() => handleFilterChange('user_only')}
          className={filter === 'user_only' ? 'active' : ''}
        >
          My Skills
        </button>
        <button 
          onClick={() => handleFilterChange('all')}
          className={filter === 'all' ? 'active' : ''}
        >
          All Skills
        </button>
      </div>

      {/* Add Skill */}
      <form onSubmit={handleAddSkill}>
        <input
          type="text"
          placeholder="Add new skill..."
          value={newSkill}
          onChange={(e) => setNewSkill(e.target.value)}
        />
        <button type="submit">Add Skill</button>
      </form>

      {/* Skills List */}
      <div>
        {skills.map((skill) => (
          <div 
            key={skill.id} 
            className={skill.is_user_skill ? 'owned' : 'suggested'}
          >
            <span>{skill.name}</span>
            <span>({skill.categories.join(', ')})</span>
            {skill.is_user_skill ? (
              <span>✓ Owned</span>
            ) : (
              <button onClick={() => addSkill(skill.name)}>
                Add to Profile
              </button>
            )}
          </div>
        ))}
      </div>

      {/* Pagination */}
      <div>
        <span>Total: {pagination.count} skills</span>
        {pagination.previous && (
          <button onClick={() => loadPage(pagination.previous)}>
            Previous
          </button>
        )}
        {pagination.next && (
          <button onClick={() => loadPage(pagination.next)}>
            Next
          </button>
        )}
      </div>
    </div>
  );
};
```

---

## Error Handling

All endpoints return standardized error responses:

```json
{
  "error": "Error message description"
}
```

### Common HTTP Status Codes
- `200 OK`: Success
- `201 Created`: Resource created successfully  
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Error Handling Example
```javascript
const handleApiError = (error, response) => {
  if (response?.status === 401) {
    // Redirect to login
    window.location.href = '/login';
  } else if (response?.status === 400) {
    // Show validation errors
    alert('Please check your input data');
  } else {
    // Generic error
    alert('Something went wrong. Please try again.');
  }
};
```

---

## Complete Integration Example

```javascript
// pages/resume/edit.js
import { useState } from 'react';
import { useAbout } from '../../hooks/useAbout';
import { usePersonalDetails } from '../../hooks/usePersonalDetails';
import { useExperiences } from '../../hooks/useExperiences';
import { useEducation } from '../../hooks/useEducation';
import { useSkills } from '../../hooks/useSkills';

const ResumeEditor = () => {
  const [activeTab, setActiveTab] = useState('about');
  
  const aboutData = useAbout();
  const personalData = usePersonalDetails();
  const experiencesData = useExperiences();
  const educationData = useEducation();
  const skillsData = useSkills();

  return (
    <div>
      <nav>
        <button onClick={() => setActiveTab('about')}>About</button>
        <button onClick={() => setActiveTab('personal')}>Personal Details</button>
        <button onClick={() => setActiveTab('experiences')}>Experiences</button>
        <button onClick={() => setActiveTab('education')}>Education</button>
        <button onClick={() => setActiveTab('skills')}>Skills</button>
      </nav>

      {activeTab === 'about' && <AboutForm {...aboutData} />}
      {activeTab === 'personal' && <PersonalDetailsForm {...personalData} />}
      {activeTab === 'experiences' && <ExperiencesManager {...experiencesData} />}
      {activeTab === 'education' && <EducationManager {...educationData} />}
      {activeTab === 'skills' && <SkillsManager {...skillsData} />}
    </div>
  );
};

export default ResumeEditor;
```

---

## Notes

1. **Authentication**: Store JWT tokens securely and handle token expiration
2. **Error Handling**: Implement comprehensive error handling for all API calls
3. **Loading States**: Show appropriate loading indicators during API calls
4. **Optimistic Updates**: Consider implementing optimistic updates for better UX
5. **Caching**: Implement proper caching strategies using React Query or SWR
6. **Validation**: Add client-side validation before making API calls
7. **Rate Limiting**: Be mindful of API rate limits and implement appropriate retry logic

This documentation provides a complete foundation for integrating these Resume API endpoints into your Next.js application.
