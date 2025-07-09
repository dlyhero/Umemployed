# Job Creation and Update Flow - API Documentation

## Overview

This document outlines the job creation and update flow for recruiters in the UmEmployed platform. The system provides two distinct workflows:

1. **Job Creation Flow** - For creating new jobs (includes ChatGPT calls for skill extraction and question generation)
2. **Job Update Flow** - For editing existing jobs (no ChatGPT calls for performance and cost efficiency)

## Job Creation Flow (Original - with AI Features)

The job creation process is divided into 4 steps:

### Step 1: Basic Job Details
**Endpoint:** `POST /api/jobs/create-step1/`

Creates a new job with basic information:
- Title
- Hire number
- Job location type (remote, onsite, hybrid)
- Job type (Full-time, Part-time, Contract, etc.)
- Location (country)
- Salary range
- Category

**Required:** Active recruiter subscription with available posting quota.

### Step 2: Job Preferences
**Endpoint:** `PATCH /api/jobs/<job_id>/create-step2/`

Updates job with additional preferences:
- Experience levels
- Weekly ranges
- Shifts

### Step 3: Job Description
**Endpoint:** `PATCH /api/jobs/<job_id>/create-step3/`

Updates job with content and **automatically extracts technical skills using AI**:
- Description
- Responsibilities
- Benefits

**AI Feature:** Calls `extract_technical_skills()` to automatically identify relevant skills from the job description.

### Step 4: Job Requirements
**Endpoint:** `PATCH /api/jobs/<job_id>/create-step4/`

Finalizes the job and **generates assessment questions using AI**:
- Requirements (selected from extracted skills)
- Level (Beginner, Mid, Expert)

**AI Features:**
- Calls `generate_questions_task()` to create assessment questions for each skill
- Sets `is_available = True` to publish the job
- Sends notifications to the recruiter

## Job Update Flow (New - No AI Calls)

For editing existing jobs without the overhead of AI processing:

### Update Step 1: Basic Details
**Endpoint:** `PATCH /api/jobs/<job_id>/update-step1/`

Updates basic job information:
- Title
- Hire number
- Job location type
- Job type
- Location
- Salary range
- Category

**Note:** No subscription checks or quotas applied during updates.

### Update Step 2: Preferences
**Endpoint:** `PATCH /api/jobs/<job_id>/update-step2/`

Updates job preferences:
- Job type
- Experience levels
- Weekly ranges
- Shifts

### Update Step 3: Description (No Skill Extraction)
**Endpoint:** `PATCH /api/jobs/<job_id>/update-step3/`

Updates job content **without** calling AI services:
- Description
- Responsibilities
- Benefits

**Important:** This endpoint does NOT extract technical skills or call ChatGPT, making it fast and cost-effective for updates.

### Update Step 4: Requirements (No Question Generation)
**Endpoint:** `PATCH /api/jobs/<job_id>/update-step4/`

Updates job requirements **without** generating new questions:
- Requirements (skills from existing extracted skills)
- Level

**Important:** This endpoint does NOT generate new assessment questions, preserving existing test data and candidate progress.

### Additional Update Endpoints

#### Toggle Job Availability
**Endpoint:** `PATCH /api/jobs/<job_id>/toggle-availability/`

Publish or unpublish a job:
```json
{
  "is_available": true/false
}
```

#### List Recruiter's Jobs
**Endpoint:** `GET /api/jobs/my-jobs/`

Returns all jobs created by the authenticated recruiter, ordered by creation date.

#### Get Recruiter's Job Details
**Endpoint:** `GET /api/jobs/my-jobs/<job_id>/`

Returns detailed information about a specific job created by the recruiter.

## Key Differences Between Creation and Update

| Feature | Job Creation | Job Update |
|---------|-------------|------------|
| Skill Extraction | ✅ Automatic via AI | ❌ Not performed |
| Question Generation | ✅ Auto-generated | ❌ Not performed |
| Subscription Check | ✅ Required | ❌ Not required |
| Posting Quota | ✅ Consumed | ❌ Not consumed |
| Performance | Slower (AI calls) | Faster (no AI) |
| Cost | Higher (OpenAI usage) | Lower (no AI) |

## Use Cases

### When to Use Job Creation Flow
- Creating a brand new job posting
- Need automatic skill extraction from job description
- Want AI-generated assessment questions
- Setting up complete job assessment pipeline

### When to Use Job Update Flow
- Editing existing job details
- Correcting typos or updating information
- Changing job requirements or level
- Quick updates without AI overhead
- Preserving existing candidate test data

## Authentication & Authorization

All endpoints require:
- User authentication (`IsAuthenticated`)
- Job ownership verification (user must be the job creator)

Job creation Step 1 additionally requires:
- Active recruiter subscription (`HasActiveSubscription`)
- Available posting quota

## Error Handling

Common error responses:

### 404 Not Found
```json
{
  "error": "Job not found or unauthorized."
}
```

### 400 Bad Request
```json
{
  "error": "One or more skill IDs are invalid."
}
```

### 403 Forbidden (Creation only)
```json
{
  "message": "You have reached your daily job posting limit for your subscription tier."
}
```

## Example Usage

### Creating a New Job
```bash
# Step 1: Create basic job
POST /api/jobs/create-step1/
{
  "title": "Senior Python Developer",
  "hire_number": 2,
  "job_location_type": "remote",
  "job_type": "Full_time",
  "location": "US",
  "salary_range": "100001-150000",
  "category": 1
}

# Step 2: Add preferences
PATCH /api/jobs/123/create-step2/
{
  "experience_levels": "3-5Years",
  "weekly_ranges": "mondayToFriday",
  "shifts": "dayShift"
}

# Step 3: Add description (AI extracts skills)
PATCH /api/jobs/123/create-step3/
{
  "description": "We're looking for a Python developer with Django experience...",
  "responsibilities": "Develop web applications, APIs...",
  "benefits": "Health insurance, remote work..."
}

# Step 4: Select requirements (AI generates questions)
PATCH /api/jobs/123/create-step4/
{
  "requirements": [1, 5, 8],
  "level": "Mid"
}
```

### Updating an Existing Job
```bash
# Update job title and salary
PATCH /api/jobs/123/update-step1/
{
  "title": "Senior Python Developer (Remote)",
  "salary_range": "150001+"
}

# Update job description (no AI processing)
PATCH /api/jobs/123/update-step3/
{
  "description": "Updated job description...",
  "benefits": "Added new benefits..."
}

# Unpublish job temporarily
PATCH /api/jobs/123/toggle-availability/
{
  "is_available": false
}
```

## Benefits of the Dual System

1. **Performance**: Updates are much faster without AI processing
2. **Cost Efficiency**: No OpenAI API calls during routine updates
3. **Data Preservation**: Existing assessments and candidate progress remain intact
4. **Flexibility**: Recruiters can make quick edits without going through the full creation process
5. **Reliability**: Updates don't depend on external AI services

This dual approach provides the best of both worlds: powerful AI-assisted job creation and efficient, fast job updates.
