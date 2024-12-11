from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.contrib.auth import password_validation


class EmailSignUpForm(UserCreationForm):
    # Add email field to form
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text='Required. Enter a valid email address.'
    )
    
    # Register email field and remove confirmation password
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password confirmation field
        del self.fields['password2']

    # Override password validation for single password signup
    def validate_passwords(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            try:
                password_validation.validate_password(password1, self.instance)
            except ValidationError as error:
                self.add_error('password1', error)

    def _post_clean(self):
        super(forms.ModelForm, self)._post_clean()
        self.validate_passwords()
    
    # Add email cleaning
    def clean_email(self):
        email = self.cleaned_data.get('email')
        UserModel = get_user_model()
        
        if UserModel.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
            
        return email
    
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        
        if commit:
            user.save()
        return user
    

class EmailAuthenticationForm(AuthenticationForm):
    # Override the username field to accept both username and email
    username = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={'autofocus': True})
    )
    
    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        
        if username is not None and password:
            # First try to authenticate with the provided credentials
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            
            # If direct authentication fails, try with email
            if self.user_cache is None:
                UserModel = get_user_model()
                try:
                    # Try to find a user with matching email
                    user = UserModel.objects.get(email=username)
                    # If found, try to authenticate with their username
                    self.user_cache = authenticate(
                        self.request,
                        username=user.username,
                        password=password
                    )
                except UserModel.DoesNotExist:
                    # No user found with this email
                    pass
            
            if self.user_cache is None:
                raise ValidationError(
                    "Please enter a correct username/email and password. "
                    "Note that both fields may be case-sensitive.",
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)
                
        return self.cleaned_data