UmEmployed
UmEmployed is a Django-based web application designed to help job seekers find employment opportunities.

Installation
To get started with UmEmployed, follow the steps below:

Clone the repository to your local machine:

git clone https://github.com/your-username/UmEmployed.git


Navigate to the project directory:

cd UmEmployed

Create a virtual environment (optional but recommended) to isolate your project dependencies:


python3 -m venv venv


Activate the virtual environment:

For Windows:

venv\Scripts\activate

For Unix/macOS:


source venv/bin/activate
Install the project dependencies:


pip install -r requirements.txt



Rename the .env.example file to .env and update the database configuration with your PostgreSQL credentials:


DATABASE_NAME=your_database_name
DATABASE_USER=your_username
DATABASE_PASSWORD=your_password
DATABASE_HOST=your_host
DATABASE_PORT=your_port


Apply the database migrations:

python manage.py migrate



Start the development server:


python manage.py runserver
Open your web browser and visit http://localhost:8000 to access the UmEmployed application.

Usage
Create an account or log in with existing credentials.
Explore job listings by category, location, or search for specific keywords.
Apply for job openings by submitting your resume and cover letter.
Manage your job applications and track their status.
Update your profile information and preferences.
Contributing
Not allowed at the moment

License
This project is licensed under the MIT License.

Acknowledgments
This project was inspired by the need to simplify the job search process.
Special thanks to the Django community for their excellent documentation and support.