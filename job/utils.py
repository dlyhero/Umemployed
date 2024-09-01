def calculate_skill_match(applicant_skills, job_skills):
    if not job_skills:  # Check if job_skills is empty
        return 0, []  # Return 0 match percentage and an empty list of missing skills

    common_skills = set(applicant_skills) & set(job_skills)
    match_percentage = (len(common_skills) / len(job_skills)) * 100
    missing_skills = list(set(job_skills) - common_skills)
    return match_percentage, missing_skills