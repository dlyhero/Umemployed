import pycountry
from django import forms

from resume.models import Language, UserLanguage, UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["country"]


class UserLanguageForm(forms.ModelForm):
    class Meta:
        model = UserLanguage
        fields = ["language"]

    def __init__(self, *args, **kwargs):
        super(UserLanguageForm, self).__init__(*args, **kwargs)
        self.fields["language"].queryset = Language.objects.all()


from resume.models import Education


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ["institution_name", "degree", "graduation_year"]


from resume.models import WorkExperience


class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = ["company_name", "role", "start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }
