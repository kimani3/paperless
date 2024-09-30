from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from .models import Department, Folder, Document
from .forms import DocumentForm, FolderForm, DepartmentForm, RegistrationForm, LoginForm
from datetime import date
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q


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
    
    return render(request, 'base.html', context)

def search(request):
    query = request.GET.get('q')
    departments = Department.objects.filter(name__icontains=query) if query else Department.objects.none()
    folders = Folder.objects.filter(Q(name__icontains=query) | Q(department__name__icontains=query)) if query else Folder.objects.none()
    documents = Document.objects.filter(Q(file_name__icontains=query) | Q(folder__name__icontains=query) | Q(folder__department__name__icontains=query)) if query else Document.objects.none()

    context = {
        'query': query,
        'departments': departments,
        'folders': folders,
        'documents': documents,
    }

    return render(request, 'documents/search_results.html', context)


@login_required
def upload_document(request, department_id=None, folder_id=None):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            if folder_id:
                folder = get_object_or_404(Folder, id=folder_id)
                document.folder = folder
            else:
                department = get_object_or_404(Department, id=department_id)
                folder_name = date.today().now().strftime('%Y-%m-%d')
                folder, created = Folder.objects.get_or_create(name=folder_name, department=department)
                document.folder = folder
            document.save()
            messages.success(request, 'Document uploaded successfully.')
            return redirect('documents:folder_detail', folder.id if folder_id else folder.id)
    else:
        form = DocumentForm()
    return render(request, 'documents/upload_document.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save(commit=False)
            department.created_by = request.user
            department.save()
            return redirect('documents:department_list')
    else:
        form = DepartmentForm()
    return render(request, 'documents/manage_department.html', {'form': form})

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
def document_list(request):
    documents = Document.objects.all()
    return render(request, 'documents/document_list.html', {'documents': documents})

@login_required
def folder_list(request):
    folders = Folder.objects.all()
    return render(request, 'documents/folder_list.html', {'folders': folders})

def folder_detail(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    documents = Document.objects.filter(folder=folder)
    return render(request, 'documents/document_details.html', {
        'department': folder.department,
        'folders': Folder.objects.filter(department=folder.department),
        'selected_folder': folder,  # Pass the selected folder
        'documents': documents,  # You can also include documents if needed
    })


@login_required
def view_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    response = HttpResponse(document.file_content, content_type='application/octet-stream')
    response['Content-Disposition'] = f'inline; filename="{document.file_name}"'
    return response

@login_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'documents/department_list.html', {'departments': departments})

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
