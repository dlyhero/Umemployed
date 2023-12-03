def calculate_skill_match(applicant_skills, job_skills):
    common_skills = applicant_skills.intersection(job_skills)
    match_percentage = (len(common_skills) / len(job_skills)) * 100
    return match_percentage, job_skills - common_skills  # Missing skills