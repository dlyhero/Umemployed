"""
REAL-WORLD EXAMPLE: Question Pool in Action

Scenario: A startup creates a "Full Stack Developer" job
Skills Required: [Python, React, PostgreSQL, Docker, Git]
Job Level: "Mid" (intermediate)
"""

# ===== STEP 1: Job Creation (Step 4 API) =====
POST /api/jobs/123/create-step4/
{
    "requirements": [15, 23, 45, 67, 89],  # Skill IDs for Python, React, etc.
    "level": "Mid"
}

# System Response:
{
    "message": "Job creation step 4 completed. Smart question generation started in background."
}

# ===== STEP 2: Background Tasks Start =====
# 5 parallel tasks launch:
smart_generate_questions_task.delay(job_id=123, skill_id=15, level="Mid")  # Python
smart_generate_questions_task.delay(job_id=123, skill_id=23, level="Mid")  # React  
smart_generate_questions_task.delay(job_id=123, skill_id=45, level="Mid")  # PostgreSQL
smart_generate_questions_task.delay(job_id=123, skill_id=67, level="Mid")  # Docker
smart_generate_questions_task.delay(job_id=123, skill_id=89, level="Mid")  # Git

# ===== STEP 3: Individual Skill Processing =====

## 🐍 PYTHON SKILL (AI Success)
"""
Task 1: Python
1. Check existing questions: 0 found
2. Try AI generation: SUCCESS! 
3. Generated 5 questions about Django, FastAPI, decorators
4. Save as SkillQuestion with source='ai_generated'
5. Mark status: 'ai_success'
"""

## ⚛️ REACT SKILL (AI Partial Failure)  
"""
Task 2: React
1. Check existing questions: 0 found
2. AI Attempt 1: FAIL (OpenAI timeout)
3. AI Attempt 2: FAIL (Rate limit hit)  
4. AI Attempt 3: SUCCESS! Generated 3 questions
5. Need 5 questions, only got 3
6. Look in QuestionPool for React + intermediate difficulty
7. Found 2 pool questions about hooks, state management
8. Total: 3 AI + 2 pool = 5 questions ✅
9. Mark status: 'ai_success' (got some AI questions)
"""

## 🐘 POSTGRESQL SKILL (Complete AI Failure → Pool Success)
"""
Task 3: PostgreSQL  
1. Check existing questions: 0 found
2. AI Attempt 1: FAIL (Invalid response format)
3. AI Attempt 2: FAIL (OpenAI service down)
4. AI Attempt 3: FAIL (Content policy violation)
5. Mark status: 'ai_failed', attempts: 3
6. Trigger fallback: use_fallback_questions()
7. Look in QuestionPool:
   - skill=PostgreSQL, difficulty=intermediate: Found 4 questions
   - Topics: Joins, Indexing, Transactions, Performance
8. Create 4 SkillQuestions with source='fallback_pool'
9. Update pool usage_count for used questions
10. Mark status: 'fallback_used' ✅
"""

## 🐳 DOCKER SKILL (No Pool Questions → Skip)
"""
Task 4: Docker
1. Check existing questions: 0 found  
2. AI Attempt 1,2,3: All FAIL
3. Look in QuestionPool for Docker: 0 found (new technology)
4. Mark status: 'skipped' 
5. This skill becomes "Portfolio Review Only"
"""

## 📝 GIT SKILL (AI Success)
"""
Task 5: Git
1. Check existing questions: 0 found
2. Try AI generation: SUCCESS!
3. Generated 5 questions about branching, merging, conflicts
4. Save as SkillQuestion with source='ai_generated'  
5. Mark status: 'ai_success'
"""

# ===== STEP 4: Job Completion Check =====
"""
Final Status Check:
- Python: ai_success ✅
- React: ai_success ✅  
- PostgreSQL: fallback_used ✅
- Docker: skipped ✅ (counts as acceptable)
- Git: ai_success ✅

Completion: 5/5 skills have acceptable status
Job marked: job_creation_is_complete = True
Email notifications sent ✅
"""

# ===== STEP 5: Candidate Experience =====
"""
When candidates apply to this job:

Python Questions: 
- 5 AI-generated, job-specific questions about web frameworks

React Questions:
- 3 AI-generated questions about modern React patterns  
- 2 Pool questions about fundamental React concepts

PostgreSQL Questions:
- 4 Pool questions covering essential database concepts

Docker Assessment:
- No technical questions
- Portfolio review section asks about containerization experience
- Resume parsing looks for Docker keywords

Git Questions:
- 5 AI-generated questions about version control workflows
"""

# ===== COST ANALYSIS =====
"""
AI Calls Made:
- Python: 1 successful call
- React: 3 attempts (2 failed, 1 partial success)  
- PostgreSQL: 3 failed attempts
- Docker: 3 failed attempts
- Git: 1 successful call

Total: 11 AI calls
Successful generations: 2.6 out of 5 skills (52% success rate)
Job completion: 100% (thanks to fallback pool)

Without Pool System:
- Job would be stuck incomplete
- Continuous retry attempts
- Much higher costs
- Poor user experience
"""
