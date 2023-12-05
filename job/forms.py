from django import forms
from .models import Job

from django import forms
from .models import Job
from resume.models import Skill, SkillCategory

class CreateJobForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=SkillCategory.objects.all(), empty_label=None)
    requirements = forms.ModelMultipleChoiceField(queryset=Skill.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Job
        fields = ['title', 'location', 'salary', 'requirements', 'ideal_candidate']
class UpdateJobForm(forms.ModelForm):
    class Meta:
        model = Job
        exclude = ('user','company')