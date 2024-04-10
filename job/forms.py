from django import forms
from .models import Job

from django import forms
from .models import Job,ApplicantAnswer
from resume.models import Skill, SkillCategory

class CreateJobForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=SkillCategory.objects.all(), empty_label=None)

    class Meta:
        model = Job
        fields = ['title','category', 'location', 'salary']

class JobDescriptionForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea)


class SkillForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['requirements', 'extracted_skills', 'level']  # Include 'extracted_skills' along with 'requirements'
        widgets = {
            'requirements': forms.CheckboxSelectMultiple(),
            'extracted_skills': forms.CheckboxSelectMultiple(),  # Add widget for 'extracted_skills' if needed
        }


    def __init__(self, *args, **kwargs):
        category = kwargs.pop('category')
        extracted_skills = kwargs.pop('extracted_skills', None)  # Get extracted_skills from kwargs
        super().__init__(*args, **kwargs)
        
        # Set queryset for 'requirements' field based on the category
        self.fields['requirements'].queryset = Skill.objects.filter(categories=category)
        
        # If extracted_skills is provided, initialize the field with it
        if extracted_skills is not None:
            self.fields['requirements'].initial = extracted_skills


class UpdateJobForm(forms.ModelForm):
    class Meta:
        model = Job
        exclude = ('user','company')

from .models import MCQ

class ApplicantAnswerForm(forms.ModelForm):
    class Meta:
        model = ApplicantAnswer  # Use the ApplicantAnswer model
        fields = '__all__'  # Specify fields for the applicant's answers

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)