def calculate_skill_match(applicant_skills, job_skills):
    if not job_skills:  # Check if job_skills is empty
        return 0, []  # Return 0 match percentage and an empty list of missing skills

    # Normalize skill names to lowercase to avoid case sensitivity issues
    applicant_skills_normalized = {skill.name.lower() for skill in applicant_skills}
    job_skills_normalized = {skill.name.lower() for skill in job_skills}

    common_skills = applicant_skills_normalized & job_skills_normalized
    match_percentage = (len(common_skills) / len(job_skills_normalized)) * 100
    missing_skills = list(job_skills_normalized - common_skills)
    
    return match_percentage, missing_skills
