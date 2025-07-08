from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm


class RegisterUserForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "email", "password1", "password2"]
        widgets = {"email": forms.EmailInput(attrs={"class": "email-input"})}


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].widget.attrs.update({"class": "form-control"})
        self.fields["new_password2"].widget.attrs.update({"class": "form-control"})
