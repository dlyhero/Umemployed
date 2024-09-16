from django import forms
from .models import Company
from django_countries.widgets import CountrySelectWidget
from django_countries.fields import CountryField
from cities_light.models import City

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

class UpdateCompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'mission_statement': forms.Textarea(attrs={'rows': 3}),
            'vision_statement': forms.Textarea(attrs={'rows': 3}),
            'job_openings': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark social fields as optional
        for field_name in ['linkedin', 'facebook', 'twitter', 'instagram', 'video_introduction']:
            self.fields[field_name].required = False

class CreateCompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'name', 'industry', 'contact_email', 'country', 'location', 
            'description', 'logo', 'size', 'contact_phone', 'mission_statement'
        ]
        widgets = {
            'country': CountrySelectWidget(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'
            }),
            'location': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'
            }, choices=[
                ('New York', 'New York'),
                ('San Francisco', 'San Francisco'),
                ('Los Angeles', 'Los Angeles'),
                ('Chicago', 'Chicago'),
                ('London', 'London'),
                # Add more locations as needed
            ]),
            'size': forms.Select(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'
            }, choices=[
                ('1-10', '1-10 employees'),
                ('11-50', '11-50 employees'),
                ('51-200', '51-200 employees'),
                ('201-500', '201-500 employees'),
                ('501-1000', '501-1000 employees'),
                ('1001-5000', '1001-5000 employees'),
                ('5001-10000', '5001-10000 employees'),
                ('10001+', '10001+ employees'),
            ]),
        }
