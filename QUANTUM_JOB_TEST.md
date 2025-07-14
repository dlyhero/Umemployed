# Quantum Computing Job Test - Postman Collection
# Testing Complete Fallback System from Step 1 to Completion

## 🎯 Test Scenario
**Job:** Senior Quantum Computing Developer  
**Skills:** Quantum Computing, Python, Machine Learning, Linear Algebra, Physics  
**Expected Behavior:** 
- Quantum Computing: AI fail → Pool fail → Generic/Experience questions
- Python: AI success (common skill)
- Machine Learning: AI success or Pool fallback
- Linear Algebra: Pool fallback or Generic questions
- Physics: Generic/Experience questions

---

## 📋 Postman Setup

### Environment Variables
Create a new Postman environment with:
```json
{
    "base_url": "http://localhost:8000/api",
    "auth_token": "",
    "job_id": "",
    "company_id": "1"
}
```

---

## 🔑 Step 0: Authentication

### Login Request
```http
POST {{base_url}}/auth/login/
Content-Type: application/json

{
    "email": "recruiter@company.com",
    "password": "your_password"
}
```

**Set auth_token in Tests:**
```javascript
pm.test("Login successful", function () {
    var jsonData = pm.response.json();
    pm.environment.set("auth_token", jsonData.access);
});
```

---

## 🔍 Step 0.5: Debug Subscription Status

⚠️ **If Step 1 fails with "This action requires a Recruiter subscription"**, run this debug request first:

```http
GET {{base_url}}/transactions/subscription-debug/
Authorization: Bearer {{auth_token}}
```

**Check Response for Issues:**
```javascript
pm.test("Debug subscription status", function () {
    var jsonData = pm.response.json();
    console.log("Subscription Debug Info:");
    console.log("User ID:", jsonData.user_id);
    console.log("Has Active Subscription:", jsonData.active_subscription.exists);
    console.log("User Type:", jsonData.active_subscription.user_type);
    console.log("Tier:", jsonData.active_subscription.tier);
    console.log("Has Recruiter Subscription:", jsonData.recruiter_subscription.exists);
    console.log("Can Create Jobs:", jsonData.permissions.can_create_jobs);
    console.log("Troubleshooting:", jsonData.troubleshooting);
    
    // Common issues:
    if (jsonData.troubleshooting.missing_recruiter_subscription) {
        console.log("❌ ISSUE: No recruiter subscription found");
        console.log("👉 SOLUTION: Create a recruiter subscription");
    }
    if (jsonData.troubleshooting.wrong_user_type) {
        console.log("❌ ISSUE: Subscription exists but user_type is not 'recruiter'");
        console.log("👉 SOLUTION: Update subscription user_type to 'recruiter'");
    }
    if (jsonData.troubleshooting.subscription_inactive) {
        console.log("❌ ISSUE: Subscription exists but is_active = false");
        console.log("👉 SOLUTION: Activate the subscription");
    }
    if (jsonData.troubleshooting.reached_daily_limit) {
        console.log("❌ ISSUE: Daily job posting limit reached");
        console.log("👉 SOLUTION: Wait for next day or upgrade tier");
    }
});
```

### Common Fixes

**Fix 1: Create Recruiter Subscription (via Django Admin)**
```sql
-- Check current subscriptions
SELECT id, user_id, user_type, tier, is_active FROM transactions_subscription WHERE user_id = YOUR_USER_ID;

-- Create recruiter subscription if missing
INSERT INTO transactions_subscription (user_id, user_type, tier, is_active, started_at) 
VALUES (YOUR_USER_ID, 'recruiter', 'premium', true, NOW());
```

**Fix 2: Update Existing Subscription**
```sql
-- Update user_type to recruiter
UPDATE transactions_subscription 
SET user_type = 'recruiter', tier = 'premium', is_active = true 
WHERE user_id = YOUR_USER_ID;
```

**Fix 3: Via Django Shell**
```python
from transactions.models import Subscription
from users.models import User

user = User.objects.get(email='your_email@example.com')

# Create recruiter subscription
subscription = Subscription.objects.create(
    user=user,
    user_type='recruiter',
    tier='premium',
    is_active=True
)

# Or update existing
subscription = Subscription.objects.filter(user=user).first()
if subscription:
    subscription.user_type = 'recruiter'
    subscription.tier = 'premium'
    subscription.is_active = True
    subscription.save()
```

---

## 🏗️ Step 1: Create Basic Job Info

```http
POST {{base_url}}/job/create-step1/
Authorization: Bearer {{auth_token}}
Content-Type: application/json

{
    "title": "Senior Quantum Computing Developer",
    "hire_number": 2,
    "job_location_type": "hybrid",
    "location": "US", 
    "salary": 180000,
    "salary_range": "150001+",
    "category": 1,
    "job_type": "Full_time"
}
```

**Save job_id in Tests:**
```javascript
pm.test("Job created", function () {
    var jsonData = pm.response.json();
    pm.environment.set("job_id", jsonData.id);
});
```

---

## 📝 Step 2: Add Job Details

```http
POST {{base_url}}/job/{{job_id}}/create-step2/
Authorization: Bearer {{auth_token}}
Content-Type: application/json

{
    "job_type": "Full_time",
    "experience_levels": "5-10Years", 
    "weekly_ranges": "mondayToFriday",
    "shifts": "dayShift"
}
```

**Valid Values:**
- `job_type`: "Full_time", "Part_time", "Contract", "Internship"
- `experience_levels`: "noExperience", "under1Year", "1-3Years", "3-5Years", "5-10Years", "10+Years"
- `weekly_ranges`: "mondayToFriday", "mondayToSaturday", "weekends", "flexible"
- `shifts`: "dayShift", "eveningShift", "nightShift", "flexible"

---

## 📋 Step 3: Add Descriptions

```http
PATCH {{base_url}}/jobs/{{job_id}}/create-step3/
Authorization: Bearer {{auth_token}}
Content-Type: application/json

{
    "description": "We are seeking a Senior Quantum Computing Developer to lead our quantum algorithm development team. You will work on cutting-edge quantum algorithms for optimization, machine learning, and cryptography applications.",
    "responsibilities": "Design and implement quantum algorithms, collaborate with physics and engineering teams, optimize quantum circuits for NISQ devices, conduct research on quantum advantage applications.",
    "ideal_candidate": "PhD in Physics, Computer Science, or related field. 5+ years experience in quantum computing. Proficiency in Qiskit, Cirq, or similar frameworks. Strong background in linear algebra and quantum mechanics.",
    "benefits": "Competitive salary, equity package, flexible work arrangements, conference attendance, research publication opportunities."
}
```

---

## 🎯 Step 4: Add Skills (Trigger Question Generation)

### First, get or create skills:

#### Get existing skills:
```http
GET {{base_url}}/skills/
Authorization: Bearer {{auth_token}}
```

#### Create Quantum Computing skill if needed:
```http
POST {{base_url}}/skills/
Authorization: Bearer {{auth_token}}
Content-Type: application/json

{
    "name": "Quantum Computing",
    "category": 1
}
```

### Main Step 4 Request:
```http
PATCH {{base_url}}/jobs/{{job_id}}/create-step4/
Authorization: Bearer {{auth_token}}
Content-Type: application/json

{
    "requirements": [101, 15, 45, 67, 89],
    "level": "Expert"
}
```

**Where IDs represent:**
- 101: Quantum Computing (specialized)
- 15: Python (common)  
- 45: Machine Learning
- 67: Linear Algebra
- 89: Physics

**Expected Response:**
```json
{
    "job": {
        "id": 123,
        "is_available": true,
        "job_creation_is_complete": false
    },
    "message": "Smart question generation started in background."
}
```

---

## 📊 Step 5: Monitor Progress (Polling)

```http
GET {{base_url}}/jobs/{{job_id}}/creation-progress/
Authorization: Bearer {{auth_token}}
```

**Auto-polling Test Script:**
```javascript
pm.test("Check completion", function () {
    var jsonData = pm.response.json();
    
    if (jsonData.is_complete === false) {
        console.log("Progress: " + jsonData.progress.percentage + "%");
        
        // Continue polling after 5 seconds
        setTimeout(() => {
            postman.setNextRequest("Monitor Progress");
        }, 5000);
    } else {
        console.log("Job complete! Final status:");
        console.log(JSON.stringify(jsonData.progress.skills_status, null, 2));
        postman.setNextRequest("Verify Job Listed");
    }
});
```

**Expected Final Response:**
```json
{
    "job_id": 123,
    "is_complete": true,
    "progress": {
        "total_skills": 5,
        "completed_skills": 5,
        "percentage": 100.0,
        "skills_status": {
            "Quantum Computing": {
                "complete": true,
                "status": "generic_used",
                "questions_count": 3,
                "ai_attempts": 3,
                "source": "generic_used"
            },
            "Python": {
                "complete": true,
                "status": "ai_success",
                "questions_count": 5,
                "ai_attempts": 1,
                "source": "ai_success"
            },
            "Machine Learning": {
                "complete": true,
                "status": "ai_success",
                "questions_count": 5,
                "ai_attempts": 2,
                "source": "ai_success"
            },
            "Linear Algebra": {
                "complete": true,
                "status": "fallback_used",
                "questions_count": 4,
                "ai_attempts": 3,
                "source": "fallback_used"
            },
            "Physics": {
                "complete": true,
                "status": "experience_based",
                "questions_count": 3,
                "ai_attempts": 3,
                "source": "experience_based"
            }
        }
    }
}
```

---

## ✅ Step 6: Verify Job Listed

```http
GET {{base_url}}/jobs/
Authorization: Bearer {{auth_token}}
```

**Test:**
```javascript
pm.test("Job appears in listing", function () {
    var jsonData = pm.response.json();
    var job = jsonData.results.find(j => j.id == pm.environment.get("job_id"));
    pm.expect(job).to.not.be.undefined;
    pm.expect(job.job_creation_is_complete).to.eql(true);
    pm.expect(job.title).to.eql("Senior Quantum Computing Developer");
});
```

---

## 🔍 Step 7: Inspect Generated Questions

```http
GET {{base_url}}/jobs/{{job_id}}/skill-questions/
Authorization: Bearer {{auth_token}}
```

**Expected Response:**
```json
{
    "job_id": 123,
    "total_questions": 20,
    "questions_by_skill": {
        "Quantum Computing": {
            "count": 3,
            "source": "generic_used",
            "questions": [
                {
                    "question": "What is the most important principle when working with Quantum Computing?",
                    "option_a": "Writing clean, maintainable code",
                    "correct_answer": "A",
                    "source": "generic"
                }
            ]
        },
        "Python": {
            "count": 5,
            "source": "ai_success",
            "questions": [
                {
                    "question": "Which Python library is commonly used for quantum computing?",
                    "option_a": "NumPy",
                    "option_b": "Qiskit",
                    "correct_answer": "B",
                    "source": "ai_generated"
                }
            ]
        }
    }
}
```

---

## 🐛 Debug: Check Your Subscription Status

Before running the main test, let's verify your subscription:

### Check Current User Info
```http
GET {{base_url}}/auth/user/
Authorization: Bearer {{auth_token}}
```

### Check Subscription Status (Add this endpoint if it doesn't exist)
```http
GET {{base_url}}/users/subscription-status/
Authorization: Bearer {{auth_token}}
```

### Alternative: Check Transactions
```http
GET {{base_url}}/transactions/my-subscriptions/
Authorization: Bearer {{auth_token}}
```

**Expected Debug Response:**
```json
{
    "user": {
        "id": 1,
        "email": "recruiter@company.com",
        "user_type": "recruiter"
    },
    "subscription": {
        "id": 123,
        "user_type": "recruiter",  // ← This must be "recruiter"
        "tier": "premium",
        "is_active": true,
        "started_at": "2025-01-01T00:00:00Z",
        "expires_at": "2025-12-31T23:59:59Z"
    }
}
```

**Common Issues:**
1. **Wrong user_type**: Subscription has `user_type: "user"` instead of `"recruiter"`
2. **Inactive subscription**: `is_active: false`
3. **Expired subscription**: Past the `expires_at` date
4. **No subscription**: No subscription record exists

---

## ✅ SUBSCRIPTION ISSUE - RESOLVED!

**Problem:** `"This action requires a Recruiter subscription"` even with valid subscription.

**Root Cause:** Permission class was selecting the newest subscription (user type) instead of the required subscription type (recruiter).

**Fix Applied:** Updated `HasActiveSubscription` permission class to filter by `required_user_type` first when specified.

**Before Fix:**
```python
# Always got the most recent subscription regardless of type
subscription = Subscription.objects.filter(user=user, is_active=True).order_by("-started_at").first()
```

**After Fix:**
```python
# Now correctly filters by required user_type first
if required_user_type:
    subscription = Subscription.objects.filter(
        user=user, user_type=required_user_type, is_active=True
    ).order_by("-started_at").first()
```

**Status:** ✅ Job creation now works! Permission error resolved.

---

## 🛠️ CORRECTED API ENDPOINTS

### Step 1: Create Job ✅
```bash
curl -X POST "http://127.0.0.1:8000/api/job/create-step1/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Quantum Computing Developer",
    "hire_number": 2,
    "job_location_type": "hybrid",
    "location": "US", 
    "salary": 180000,
    "salary_range": "150001+",
    "category": 1,
    "job_type": "Full_time"
  }'
```

### Step 2: Add Job Details ✅
```bash
curl -X POST "http://127.0.0.1:8000/api/job/{JOB_ID}/create-step2/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_type": "Full_time",
    "experience_levels": "5-10Years", 
    "weekly_ranges": "mondayToFriday",
    "shifts": "dayShift"
  }'
```

**Key Corrections Made:**
1. Fixed subscription permission logic ✅
2. Added missing `job_type` field to step 1 ✅  
3. Corrected `experience_level` → `experience_levels` ✅
4. Used correct URL endpoints ✅

---

## 🎯 Success Criteria

✅ **Job Creation:** All 4 steps complete successfully  
✅ **Question Generation:** Background tasks start immediately  
✅ **Fallback System:** All skills get questions via appropriate fallback  
✅ **Job Completion:** `job_creation_is_complete: true`  
✅ **Job Visibility:** Job appears in public listings  
✅ **Question Diversity:** Multiple question sources (AI, pool, generic, experience)  

---

## 🚀 Expected Fallback Behavior

### Quantum Computing (New/Specialized)
- ❌ AI Generation: Fails (insufficient training data)
- ❌ Pool Questions: Empty (too new/specialized)
- ✅ Generic Questions: 3 universal programming questions
- ✅ Experience Questions: 2 experience-level questions

### Python (Common Skill)
- ✅ AI Generation: Succeeds immediately
- 5 job-specific Python questions generated

### Machine Learning (Moderately Common)
- ✅ AI Generation: Succeeds after 1-2 attempts
- 5 ML-specific questions generated

### Linear Algebra (Mathematical)
- ❌ AI Generation: Fails (too academic)
- ✅ Pool Questions: 4 pre-made math questions
- From existing question pool

### Physics (Academic Field)
- ❌ AI Generation: Fails (too broad)
- ❌ Pool Questions: Limited coverage
- ✅ Experience Questions: 3 experience-based assessments

This test demonstrates that your system gracefully handles even the most challenging skill combinations while maintaining 100% job completion rate! 🌟
