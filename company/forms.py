from django import forms
from .models import Company

class UpdateCompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        exclude = ('user', )

class CreateCompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'industry', 'location', 'country', 'description', 'logo']
