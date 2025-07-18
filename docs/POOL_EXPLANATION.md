# Question Pool System Explanation

## 🏗️ ARCHITECTURE

### Question Pool Model (QuestionPool)
```python
class QuestionPool:
    skill = "Python"                    # Which skill this question tests
    question = "What is a decorator?"   # The actual question
    option_a = "A function modifier"    # Multiple choice options
    option_b = "A design pattern"
    option_c = "A loop construct" 
    option_d = "A data type"
    correct_answer = "A"               # Correct answer
    difficulty = "advanced"            # beginner/intermediate/advanced
    area = "Advanced Concepts"         # Sub-area of the skill
    usage_count = 0                   # How many times used (for rotation)
    is_active = True                  # Can be disabled if outdated
```

## 🔄 THE SMART FLOW

### Step 1: Job Creation (Step 4)
```
User selects skills: [Python, React, SQL]
System starts: smart_generate_questions_task() for each skill
```

### Step 2: For Each Skill - Try AI First
```python
# For Python skill:
1. Check if questions already exist ✓
2. Try AI generation (max 3 attempts)
   - Attempt 1: Call OpenAI API
   - Attempt 2: Wait 5 minutes, try again  
   - Attempt 3: Wait 10 minutes, try again
```

### Step 3: AI Success Path
```python
if ai_generation_successful:
    # Save as SkillQuestion with source='ai_generated'
    save_questions_to_db(questions, source='ai_generated')
    mark_skill_status('ai_success')
```

### Step 4: AI Failure Path - Use Pool
```python
if ai_failed_3_times:
    # Look for pre-made questions in pool
    pool_questions = QuestionPool.objects.filter(
        skill=skill,
        difficulty=map_level_to_difficulty(job.level),
        is_active=True
    ).order_by('usage_count')  # Use least-used first
    
    # Convert pool questions to job-specific questions
    for pool_q in pool_questions:
        SkillQuestion.objects.create(
            question=pool_q.question,
            option_a=pool_q.option_a,
            # ... copy all fields
            job=current_job,
            source='fallback_pool'  # Mark as pool-sourced
        )
        
        pool_q.usage_count += 1  # Track usage for rotation
        pool_q.save()
```

## 📚 POOL POPULATION

### Pre-populated with Common Questions
```python
# For Python skill, we pre-create questions like:
QuestionPool.objects.create(
    skill=python_skill,
    question="What is the output of print(type([]))?",
    option_a="<class 'list'>",
    option_b="<class 'array'>", 
    option_c="list",
    option_d="array",
    correct_answer="A",
    difficulty="beginner"
)
```

### Management Command
```bash
# Populate pool with 100+ common questions
python manage.py populate_question_pool

# Populate specific skill
python manage.py populate_question_pool --skill Python

# Clear and repopulate
python manage.py populate_question_pool --clear
```

## 🎯 SMART FEATURES

### 1. Difficulty Mapping
```python
job.level = "Beginner" → pool.difficulty = "beginner"
job.level = "Mid"      → pool.difficulty = "intermediate"  
job.level = "Expert"   → pool.difficulty = "advanced"
```

### 2. Usage Rotation
```python
# Always use least-used questions first
order_by('usage_count')  # Questions with usage_count=0 first
```

### 3. Graceful Degradation
```python
# Try exact difficulty first
pool_questions = QuestionPool.filter(skill=skill, difficulty=exact_level)

if not pool_questions.exists():
    # Fallback to any difficulty for this skill
    pool_questions = QuestionPool.filter(skill=skill)
```

### 4. Source Tracking
```python
# Every question knows its source
SkillQuestion.source = 'ai_generated'    # Best quality
SkillQuestion.source = 'fallback_pool'   # Good quality  
SkillQuestion.source = 'manual'          # Admin added
```

## 💰 COST BENEFITS

### Before Pool System:
```
Job with 5 skills:
- Python: AI success (1 call) ✅
- React: AI fails 10 times (10 calls) ❌ 
- SQL: Never tried because React stuck ❌
- Job never completes ❌
Total: 11 AI calls, 0 completed jobs
```

### With Pool System:
```
Job with 5 skills:
- Python: AI success (1 call) ✅
- React: AI fails 3 times, use pool (3 calls + pool) ✅
- SQL: AI success (1 call) ✅  
- Job completes successfully ✅
Total: 5 AI calls, 1 completed job
```

## 🔍 QUALITY LEVELS

### Tier 1: AI Generated (Best)
- Job-specific context
- Latest technologies  
- Tailored difficulty

### Tier 2: Pool Questions (Good)
- Skill-specific
- Professionally written
- Covers fundamentals

### Tier 3: Portfolio Review (Fallback)
- No technical questions
- Resume/portfolio based
- Still allows job completion

## 📊 MONITORING

### Track Pool Usage
```python
# Most used questions (may need refreshing)
QuestionPool.objects.order_by('-usage_count')

# Unused questions (good variety)  
QuestionPool.objects.filter(usage_count=0)

# Skills with no pool questions (need attention)
skills_without_pool = Skill.objects.exclude(
    id__in=QuestionPool.objects.values('skill_id')
)
```

### Success Rates
```python
ai_generated = SkillQuestion.objects.filter(source='ai_generated').count()
pool_used = SkillQuestion.objects.filter(source='fallback_pool').count()

print(f"AI Success Rate: {ai_generated/(ai_generated+pool_used)*100:.1f}%")
```
