# forms.py
from django import forms

from .models import Assessment, Option, Question


class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ["title", "description", "duration"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["question_text"]
        widgets = {
            "question_text": forms.Textarea(attrs={"rows": 4}),
        }


class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ["option_text", "is_correct"]
