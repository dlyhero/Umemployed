from django import forms
from .models import Resume, SkillCategory, Skill, Experience, Education

class UpdateResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['first_name', 'surname', 'date_of_birth', 'phone', 'state', 'country', 'job_title']

class UpdateResumeForm2(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=SkillCategory.objects.all(), empty_label=None)
    skills = forms.ModelMultipleChoiceField(queryset=Skill.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Resume
        fields = ['date_of_birth', 'phone', 'description', 'category', 'skills', 'profile_image']

class UpdateResumeForm3(forms.ModelForm):
    experience_company_name = forms.CharField(max_length=100)
    experience_years = forms.CharField(max_length=100)
    education_institution_name = forms.CharField(max_length=100)
    education_degree = forms.CharField(max_length=100)
    education_graduation_year = forms.IntegerField()

    cv = forms.FileField(widget=forms.FileInput(attrs={'accept': '.pdf'}))

    class Meta:
        model = Resume
        fields = ['cv']

    def save(self, commit=True):
        resume = super().save(commit=False)

        experience_company_name = self.cleaned_data['experience_company_name']
        experience_years = self.cleaned_data['experience_years']
        education_institution_name = self.cleaned_data['education_institution_name']
        education_degree = self.cleaned_data['education_degree']
        education_graduation_year = self.cleaned_data['education_graduation_year']

        experience = Experience.objects.create(
            resume=resume,
            company_name=experience_company_name,
            years=experience_years
        )
        education = Education.objects.create(
            resume=resume,
            institution_name=education_institution_name,
            degree=education_degree,
            graduation_year=education_graduation_year
        )

        if commit:
            resume.save()

        return resume