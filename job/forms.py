from django import forms
from .models import Job

from django import forms
from .models import Job,ApplicantAnswer
from resume.models import Skill, SkillCategory

class CreateJobForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=SkillCategory.objects.all(), empty_label=None)

    class Meta:
        model = Job
        fields = ['title','category', 'location', 'salary', 'description']

class SkillForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['requirements', 'level']
        widgets = {
            'requirements': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        category = kwargs.pop('category')
        super().__init__(*args, **kwargs)
        self.fields['requirements'].queryset = Skill.objects.filter(categories=category)

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