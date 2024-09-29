# custom_admin_dashboard/forms.py
from django import forms
from django.contrib.auth.models import User
from documents.models import Department, Folder, Document

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_superuser']  # Add any fields you need

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'department']

class DocumentForm(forms.ModelForm):
    # Create a file field for uploading files
    file = forms.FileField(label='Upload File')

    class Meta:
        model = Document
        fields = ['file_name', 'folder', 'file']  # Exclude 'file_content'

    def save(self, commit=True):
        # Override the save method to handle the file upload
        document = super().save(commit=False)
        uploaded_file = self.cleaned_data.get('file')
        
        if uploaded_file:
            # Save the uploaded file as binary content
            document.file_content = uploaded_file.read()
        
        if commit:
            document.save()
        return document
