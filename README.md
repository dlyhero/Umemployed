# Umemployed

A modern platform connecting job seekers with recruiters, featuring resume management, job listings, and recruitment tools.

## Overview

Umemployed is a comprehensive employment platform that streamlines the job search and recruitment process. The platform serves both job seekers and recruiters with specialized features for each user type.

### Key Features

- **For Job Seekers**:
  - Profile and resume management
  - Job search and application
  - Skill assessment
  - Interview scheduling

- **For Recruiters**:
  - Company profile management
  - Job posting and management
  - Candidate search and filtering
  - Interview scheduling

## Tech Stack

- **Backend**: Django REST Framework
- **Database**: PostgreSQL (production), SQLite (development)
- **Task Queue**: Celery with Redis
- **Real-time Communication**: Django Channels
- **Authentication**: JWT with SimpleJWT
- **Frontend**: Separate React/Next.js application
- **Deployment**: Docker, Azure App Service

## Setup and Installation

### Prerequisites

- Python 3.8+
- Redis
- PostgreSQL (for production)

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/umemployed.git
   cd umemployed
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the example environment file and configure your environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run database migrations:
   ```bash
   python manage.py migrate
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

7. Start Celery worker (in a separate terminal):
   ```bash
   celery -A umemployed worker -l info
   ```

### Docker Setup

To run the application using Docker:

```bash
docker-compose up -d
```

## API Documentation

API documentation is available at `/api/docs/` when the server is running.

## Testing

Run the test suite with:

```bash
pytest
```

## Deployment

The application is configured for deployment to Azure App Service using GitHub Actions. See the `.github/workflows/` directory for deployment configuration.

## Project Structure

```
umemployed/
├── api/                  # API endpoints and serializers
├── asseessments/         # Assessment module
├── company/              # Company management module
├── dashboard/            # User dashboard module
├── job/                  # Job listing and search module
├── messages/             # User messaging module
├── messaging/            # Additional messaging features
├── notifications/        # Notification system
├── resume/               # Resume management module
├── social_features/      # Social networking features
├── static/               # Static files
├── templates/            # HTML templates
├── transactions/         # Payment and subscription module
├── umemployed/           # Project configuration
├── users/                # User management module
├── videochat/            # Video conferencing module
└── website/              # Public website pages
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature/my-new-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This project was inspired by the need to simplify the job search process. Special thanks to the Django community for their excellent documentation and support.
