from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from .models import Department, Folder, Document, CustomUser
from .forms import DocumentForm, FolderForm, DepartmentForm, RegistrationForm, LoginForm
from datetime import date
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q

import base64
import os

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect('documents:login')  # Redirect to login after registration
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Check if the user is a superuser
                if user.is_superuser:
                    return redirect('custom_admin_dashboard:admin_dashboard')  # Redirect to custom admin dashboard
                else:
                    return redirect('documents:home')  # Redirect to home for regular users
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def home(request):
    # Fetch all departments for the user
    departments = Department.objects.all()  # Adjust this as necessary (e.g., filter by user permissions)

    # Prepare the context to be passed to the template
    context = {
        'departments': departments,
        'messages': messages.get_messages(request),  # If using Django messages framework
    }
    
    return render(request, 'documents/documents_dashboard.html', context)


def search(request):
    query = request.GET.get('q')

    # Check for exact matches first
    departments = Department.objects.filter(name__icontains=query) if query else Department.objects.none()
    folders = Folder.objects.filter(name__icontains=query) if query else Folder.objects.none()
    documents = Document.objects.filter(file_name__icontains=query) if query else Document.objects.none()

    context = {
        'query': query,
        'departments': departments,
        'folders': folders,
        'documents': documents,
    }

    return render(request, 'documents/search_results.html', context)

@login_required
def view_document_content(request, document_id):
    document = get_object_or_404(Document, id=document_id)

    # Decode the base64 encoded file content
    file_content = base64.b64decode(document.file_content)

    # Set the content type based on the file extension
    content_type = 'application/octet-stream'
    is_pdf = False
    is_image = False
    is_docx = False

    if document.file_extension == '.pdf':
        content_type = 'application/pdf'
        is_pdf = True
    elif document.file_extension in ['.jpg', '.jpeg', '.png']:
        content_type = 'image/jpeg'
        is_image = True
    elif document.file_extension == '.docx':
        content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        is_docx = True

    # Encode the file content in base64 to use in the iframe source
    base64_file_content = base64.b64encode(file_content).decode('utf-8')

    return render(request, 'documents/document_content.html', {
        'document': document,
        'file_content': base64_file_content,
        'content_type': content_type,
        'is_pdf': is_pdf,
        'is_image': is_image,
        'is_docx': is_docx,
    })



@login_required
def upload_document(request, department_id=None, folder_id=None):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)  # Save the document instance without committing

            # Get the uploaded file from the form
            uploaded_file = request.FILES.get('file_content')  # Access the file from request.FILES

            if uploaded_file:
                # Read the file data
                document_data = uploaded_file.read()  # Read the binary content of the uploaded file
                
                # Encode the file content
                document.file_content = base64.b64encode(document_data)  # Encode and assign it to the document

                # Assign the current user to the created_by field
                document.created_by = request.user

                # Get the file extension and ensure it includes the leading dot
                file_extension = os.path.splitext(uploaded_file.name)[1]
                document.file_extension = file_extension

                if folder_id:
                    folder = get_object_or_404(Folder, id=folder_id)
                    document.folder = folder
                else:
                    department = get_object_or_404(Department, id=department_id)
                    folder_name = date.today().strftime('%Y-%m-%d')
                    folder, created = Folder.objects.get_or_create(name=folder_name, department=department)
                    document.folder = folder

                # Save the document instance
                document.save()
                messages.success(request, 'Document uploaded successfully.')
                return redirect('documents:folder_detail', folder.id if folder_id else folder.id)
            else:
                messages.error(request, 'No file uploaded.')
        else:
            messages.error(request, 'Form is not valid.')
    else:
        form = DocumentForm()

    return render(request, 'documents/upload_document.html', {'form': form})


@login_required
def create_folder(request):
    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.name = date.today().strftime('%Y-%m-%d')
            folder.created_by = request.user
            folder.save()
            return redirect('documents:folder_list')
    else:
        form = FolderForm()
    return render(request, 'documents/create_folder.html', {'form': form})



@login_required
def folder_detail(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    department_id = folder.department.id  # Assuming Folder has a ForeignKey to Department

    documents = Document.objects.filter(folder=folder)  # Fetch documents in the folder

    return render(request, 'documents/document_list.html', {
        'documents': documents,
        'department_id': department_id,
        'folder': folder,  # Pass folder for ID
    })


@login_required
def department_detail(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    # Get all folders related to this department
    folders = department.folders.all()
    # Get all documents in those folders
    documents = Document.objects.filter(folder__department=department)

    return render(request, 'documents/department_details.html', {
        'department': department,
        'folders': folders,
        'documents': documents,
    })


def user_logout(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('documents:login')  # Redirect to login after logout
