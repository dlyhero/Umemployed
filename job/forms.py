from django import forms
from .models import Job

from django import forms
from .models import Job
from resume.models import Skill, SkillCategory

class CreateJobForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=SkillCategory.objects.all(), empty_label=None)

    class Meta:
        model = Job
        fields = ['title','level','category', 'location', 'salary', 'ideal_candidate']

class SkillForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['requirements']
        widgets = {
            'skills': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        category = kwargs.pop('category')
        super().__init__(*args, **kwargs)
        self.fields['requirements'].queryset = Skill.objects.filter(categories=category)


class UpdateJobForm(forms.ModelForm):
    class Meta:
        model = Job
        exclude = ('user','company')