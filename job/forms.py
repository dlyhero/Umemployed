from django import forms
from .models import Job, ApplicantAnswer, MCQ
from resume.models import Skill, SkillCategory

class CreateJobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'hire_number', 'job_type', 'location', 'salary', 'category']

    category = forms.ModelChoiceField(queryset=SkillCategory.objects.all())
class JobDescriptionForm(forms.Form):
    """
    Form for entering job description.

    Attributes:
        description (CharField): Textarea field for job description.
    """
    description = forms.CharField(widget=forms.Textarea)
    

class JobTypeForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['job_type', 'experience_levels', 'weekly_ranges', 'shifts']
        widgets = {
            'job_type': forms.HiddenInput(),
            'experience_levels': forms.HiddenInput(),
            'weekly_ranges': forms.HiddenInput(),
            'shifts': forms.HiddenInput(),
        }

from django import forms
from .models import Job, Skill

class SkillForm(forms.ModelForm):
    """
    Form for entering required skills for a job.

    Attributes:
        extracted_skills (CheckboxSelectMultiple): Checkbox field for selecting extracted skills.
        level (ChoiceField): Field for selecting the skill level.
    """
    LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Mid', 'Mid'),
        ('Expert', 'Expert'),
    ]

    level = forms.ChoiceField(choices=LEVEL_CHOICES)

    class Meta:
        model = Job
        fields = ['extracted_skills', 'level']
        widgets = {
            'extracted_skills': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        job_instance = kwargs.pop('job_instance')
        super().__init__(*args, **kwargs)
        
        # Initialize extracted_skills with the job's extracted skills
        if job_instance.extracted_skills.exists():
            self.fields['extracted_skills'].initial = job_instance.extracted_skills.all()

    def clean(self):
        cleaned_data = super().clean()
        # Perform additional validation if necessary
        return cleaned_data



class UpdateJobForm(forms.ModelForm):
    """
    Form for updating job details.

    Excludes 'user' and 'company' fields.

    Attributes:
        model (Job): The Job model.
        exclude (tuple): Fields to exclude from the form.
    """
    class Meta:
        model = Job
        exclude = ('user', 'company')

class ApplicantAnswerForm(forms.ModelForm):
    """
    Form for entering applicant's answers to MCQs.

    Attributes:
        model (ApplicantAnswer): The ApplicantAnswer model.
        fields (list): All fields of the ApplicantAnswer model.
    """
    class Meta:
        model = ApplicantAnswer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """
        Initialize the form.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
