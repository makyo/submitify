from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    """A form for registering as a new user"""
    email = forms.EmailField(
        label='Email address',
        required=True,
        help_text="""This email will be used as the primary means of
        contacting you, and will not be shared.""",
        widget=forms.EmailInput(attrs={'placeholder': 'user@example.com'}))

    class Meta:
        model = User
        fields = ('username', 'email')
        field_classes = {
            'username': UsernameField,
            'email': forms.EmailField,
        }
