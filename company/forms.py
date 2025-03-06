from django import forms
from .models import Company
from django_countries.widgets import CountrySelectWidget
from django_countries.fields import CountryField
from cities_light.models import City
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django_ckeditor_5.widgets import CKEditor5Widget

from job.models import Rating

class UpdateCompanyForm(forms.ModelForm):
    country = CountryField().formfield()  # Include this if using CountryField
    description = forms.CharField(widget=CKEditor5Widget(attrs={
        'class': 'mt-1 border bg-transparent border-gray-400 block w-full p-2 outline-1 outline-[#1e90ff] rounded-md'
    }))
    mission_statement = forms.CharField(widget=CKEditor5Widget(attrs={
        'class': 'mt-1 border bg-transparent border-gray-400 block w-full p-2 outline-1 outline-[#1e90ff] rounded-md'
    }))

    class Meta:
        model = Company
        fields = [
            'name', 'industry', 'size', 'location', 
            'founded', 'website_url', 'contact_email', 
            'contact_phone', 'linkedin', 
            'video_introduction', 'country', 'description', 
            'mission_statement'
        ]
        widgets = {
            'founded': forms.NumberInput(attrs={'placeholder': 'e.g. 2024', 'class': 'w-full mt-1 border border-gray-400 bg-transparent p-2 rounded-md'}),
            'name': forms.TextInput(attrs={
                'class': 'w-full mt-1 border border-gray-400 bg-transparent p-2 rounded-md',
                'placeholder': 'Company Name'
            }),
            'industry': forms.Select(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'size': forms.Select(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md'}),
            'location': forms.TextInput(attrs={
                'class': 'w-full mt-1 border border-gray-400 bg-transparent p-2 rounded-md',
                'placeholder': 'Company Location'
            }),
            'website_url': forms.URLInput(attrs={
                'class': 'w-full mt-1 border border-gray-400 bg-transparent p-2 rounded-md',
                'placeholder': 'https://www.example.com'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'w-full mt-1 border border-gray-400 bg-transparent p-2 rounded-md',
                'placeholder': 'Contact Email'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'w-full mt-1 border border-gray-400 bg-transparent p-2 rounded-md',
                'placeholder': 'Contact Phone'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': 'w-full mt-1 border border-gray-400 bg-transparent p-2 rounded-md',
                'placeholder': 'LinkedIn Profile'
            }),
            'video_introduction': forms.URLInput(attrs={
                'class': 'w-full mt-1 border border-gray-400 bg-transparent p-2 rounded-md',
                'placeholder': 'Video URL'
            }),
            'country': forms.Select(attrs={
                'class': 'w-full border border-gray-300 rounded-lg p-2 text-gray-700 bg-transparent focus:ring-1 focus:ring-blue-500',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark social fields as optional
        for field_name in ['linkedin', 'video_introduction']:
            if field_name in self.fields:  # Check if the field exists
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

    def clean_contact_email(self):
        email = self.cleaned_data.get('contact_email')
        if not email:
            raise forms.ValidationError('This field is required.')
        return email

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError('This field is required.')
        return name

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if not logo:
            raise forms.ValidationError('This field is required.')
        return logo

# for recruiter rating a candidate    
class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['stars', 'review', 'professionalism', 'skills', 'communication', 'teamwork', 'reliability']
        widgets = {
            'stars': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'review': forms.Textarea(attrs={'rows': 4}),
            'professionalism': forms.Select(choices=[('Excellent', 'Excellent'), ('Good', 'Good'), ('Average', 'Average'), ('Below Average', 'Below Average')]),
            'skills': forms.RadioSelect(choices=[('Yes', 'Yes'), ('No', 'No')]),
            'communication': forms.Select(choices=[('Excellent', 'Excellent'), ('Good', 'Good'), ('Average', 'Average'), ('Below Average', 'Below Average')]),
            'teamwork': forms.Select(choices=[('Excellent', 'Excellent'), ('Good', 'Good'), ('Average', 'Average'), ('Below Average', 'Below Average')]),
            'reliability': forms.Select(choices=[('Excellent', 'Excellent'), ('Good', 'Good'), ('Average', 'Average'), ('Below Average', 'Below Average')]),
        }
