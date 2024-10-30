from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Document, Folder, Department, Profile, VerificationCode
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, validate_email
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

CustomUser = get_user_model()

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        error_messages={
            'invalid': 'Please enter a valid email address.',
        },
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email'
        })
    )
    password1 = forms.CharField(
        label="Password",  # Custom label
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter password'
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",  # Custom label
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm password'
        })
    )

    email_regex = RegexValidator(
        regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        message='Please enter a valid email address. This field should be in the format example@domain.com.'
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        validate_email(email)  # First, use built-in validation
        self.email_regex(email)  # Then apply regex validation
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        try:
            validate_password(password)  # Use Django's password validators
        except ValidationError as e:
            self.add_error('password1', e)
        return password

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2')


class VerificationForm(forms.ModelForm):
    code = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter verification code'
        })
    )
    
    class Meta:
        model = VerificationCode
        fields = ['code']


class ProfileCompletionForm(forms.ModelForm):
    nationalID = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your National ID'
        })
    )
    
    contact_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your contact number'
        })
    )

    class Meta:
        model = Profile
        fields = ['nationalID', 'contact_number']
        widgets = {
            'profile_image': forms.ClearableFileInput(attrs={
                'accept': 'image/*'
            }),
        }


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter password'
        })
    )


class DocumentForm(forms.ModelForm):
    file_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter file name'
        })
    )

    class Meta:
        model = Document
        fields = ['file_name']
        widgets = {
            'file_content': forms.ClearableFileInput(attrs={
                'accept': 'application/pdf,image/*,application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }),
        }


class FolderForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter folder name'
        })
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label="Select Department"
    )

    class Meta:
        model = Folder
        fields = ['name', 'department']


class DepartmentForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter department name'
        })
    )

    class Meta:
        model = Department
        fields = ['name']
