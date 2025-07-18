# Languages, Education & Work Experience API

## Languages

### Get Available Languages (Dropdown)
**GET** `/api/resume/languages-list/`
```json
[
  {"id": 1, "name": "English"},
  {"id": 2, "name": "Spanish"},
  {"id": 3, "name": "French"}
]
```

### Get Proficiency Levels (Dropdown)
**GET** `/api/resume/proficiency-levels/`
```json
{
  "proficiency_levels": [
    {"value": "beginner", "label": "Beginner"},
    {"value": "intermediate", "label": "Intermediate"},
    {"value": "advanced", "label": "Advanced"},
    {"value": "native", "label": "Native"}
  ]
}
```

### Get User's Languages
**GET** `/api/resume/languages/`
```json
[
  {
    "id": 1,
    "language": {"id": 1, "name": "English"},
    "proficiency": "Native"
  }
]
```

### Add Language
**POST** `/api/resume/languages/`
```json
{
  "language_id": 1,
  "proficiency": "Native"
}
```

### Update Language
**PUT** `/api/resume/languages/{id}/`
```json
{
  "language_id": 2,
  "proficiency": "Fluent"
}
```

### Delete Language
**DELETE** `/api/resume/languages/{id}/`

---

## Education

### Get User's Education
**GET** `/api/resume/educations/`
```json
[
  {
    "id": 1,
    "institution_name": "University of London",
    "degree": "Bachelor of Computer Science",
    "field_of_study": "Computer Science",
    "graduation_year": 2017
  }
]
```

### Add Education
**POST** `/api/resume/educations/`
```json
{
  "institution_name": "Stanford University",
  "degree": "Master of Science",
  "field_of_study": "Computer Science",
  "graduation_year": 2020
}
```

### Update Education
**PUT** `/api/resume/educations/{id}/`
```json
{
  "institution_name": "MIT",
  "degree": "PhD",
  "field_of_study": "Artificial Intelligence",
  "graduation_year": 2023
}
```

### Delete Education
**DELETE** `/api/resume/educations/{id}/`

---

## Work Experience

### Get User's Work Experience
**GET** `/api/resume/work-experiences/`
```json
[
  {
    "id": 1,
    "company_name": "Tech Corp",
    "role": "Software Engineer",
    "start_date": "2020-01-01",
    "end_date": "2023-01-01",
    "description": "Developed web applications"
  }
]
```

### Add Work Experience
**POST** `/api/resume/work-experiences/`
```json
{
  "company_name": "Google",
  "role": "Senior Developer",
  "start_date": "2023-01-01",
  "end_date": null,
  "description": "Leading development team"
}
```

### Update Work Experience
**PUT** `/api/resume/work-experiences/{id}/`
```json
{
  "company_name": "Microsoft",
  "role": "Lead Developer",
  "start_date": "2022-01-01",
  "end_date": "2024-01-01",
  "description": "Managed development projects"
}
```

### Delete Work Experience
**DELETE** `/api/resume/work-experiences/{id}/`

---

**Note:** All endpoints require authentication. Use `PATCH` for partial updates instead of `PUT` for full updates. 