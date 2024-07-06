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

class SkillForm(forms.ModelForm):
    """
    Form for entering required skills for a job.

    Attributes:
        requirements (CheckboxSelectMultiple): Checkbox field for selecting required skills.
        extracted_skills (CheckboxSelectMultiple): Checkbox field for selecting extracted skills.
    """
    class Meta:
        model = Job
        fields = ['requirements', 'extracted_skills', 'level']
        widgets = {
            'requirements': forms.CheckboxSelectMultiple(),
            'extracted_skills': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize the form.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        category = kwargs.pop('category')
        extracted_skills = kwargs.pop('extracted_skills', None)
        super().__init__(*args, **kwargs)
        
        # Set queryset for 'requirements' field based on the category
        self.fields['requirements'].queryset = Skill.objects.filter(categories=category)
        
        # If extracted_skills is provided, initialize the field with it
        if extracted_skills is not None:
            self.fields['requirements'].initial = extracted_skills

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
