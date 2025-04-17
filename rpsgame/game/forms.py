from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class CustomUserCreationForm(UserCreationForm):
    # VULNERABILITY: Identification and Authentication Failures
    # Remove password validation
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    # skips the call to django.contrib.auth.password_validation.validate_password()
    def _post_clean(self):
        from django.forms.models import ModelForm
        ModelForm._post_clean(self)

    def clean_password2(self):
        # Override Django's password validation to allow any password
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("Passwords don't match")
        return p2

    # FIX:
    # remove everything but 'class Meta' and let Django's default validation work 