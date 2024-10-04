# documents/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Document, Folder, Department, CustomUser
from django.core.validators import RegexValidator, validate_email


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        error_messages={
            'invalid': 'Please enter a valid email address.',
        }
    )

    email_regex = RegexValidator(
        regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        message='Please enter a valid email address. This field should be in the format example@domain.com.'
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # First, let the built-in EmailField validate the format
        validate_email(email)

        # Then, apply the regex validator
        self.email_regex(email)

        return email

    class Meta:
        model = CustomUser
        fields = ('email',  'password1', 'password2')  # Ensure username is also included


class VerificationForm(forms.Form):
    code = forms.CharField(max_length=4, required=True)

class ProfileStep1Form(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['nationalID', 'department']  # Include the necessary fields
        widgets = {
            'profile_image': forms.ClearableFileInput(attrs={
                'accept': 'image/*'  # Accept only image files
            }),
        }

class ProfileStep2Form(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['contact_number']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file_name']  # Include the necessary fields
        widgets = {
            'file_content': forms.ClearableFileInput(attrs={
                'accept': 'application/pdf,image/*,application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }),
        }

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name']  # Include only the fields you want the user to fill

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']
