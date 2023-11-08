from django import forms
from .models import Resume

class UpdateResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['first_name', 'surname', 'state','country', 'job_title','profile_image', 'cv']
        widgets = {
            'cv': forms.FileInput(attrs={'accept': '.pdf'}),
        }
class UpdateResumeForm2(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['date_of_birth','phone','description','category','skills']

class UpdateResumeForm3(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['experience','education']