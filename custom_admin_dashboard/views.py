from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from documents.models import Department, Folder, Document
from django.contrib.auth.models import User
from .forms import DepartmentForm, FolderForm, DocumentForm, UserForm
from django.db.models import Q

def admin_required(login_url=None):
    return user_passes_test(lambda u: u.is_superuser, login_url=login_url)

@login_required
@admin_required(login_url='/login/')
def admin_dashboard(request):
    return render(request, 'custom_admin_dashboard/admin_dashboard.html')

@login_required
@admin_required(login_url='/login/')
def admin_departments(request):
    departments = Department.objects.all()
    return render(request, 'custom_admin_dashboard/admin_departments.html', {'departments': departments})

@login_required
@admin_required(login_url='/login/')
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
    
    return render(request, 'custom_admin_dashboard/search_results.html', context)

@login_required
@admin_required(login_url='/login/')
def admin_add_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department added successfully.')
            return redirect('custom_admin_dashboard:admin_departments')
    else:
        form = DepartmentForm()
    return render(request, 'custom_admin_dashboard/admin_add_department.html', {'form': form})

@login_required
@admin_required(login_url='/login/')
def admin_edit_department(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully.')
            return redirect('custom_admin_dashboard:admin_departments')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'custom_admin_dashboard/admin_edit_department.html', {'form': form, 'department': department})

@login_required
@admin_required(login_url='/login/')
def admin_delete_department(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    if request.method == 'POST':
        department.delete()
        messages.success(request, 'Department deleted successfully.')
        return redirect('custom_admin_dashboard:admin_departments')
    return render(request, 'custom_admin_dashboard/admin_delete_department.html', {'department': department})

@login_required
@admin_required(login_url='/login/')
def admin_folders(request):
    folders = Folder.objects.all()
    return render(request, 'custom_admin_dashboard/admin_folders.html', {'folders': folders})

@login_required
@admin_required(login_url='/login/')
def admin_add_folder(request):
    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Folder added successfully.')
            return redirect('custom_admin_dashboard:admin_folders')
    else:
        form = FolderForm()
    return render(request, 'custom_admin_dashboard/admin_add_folder.html', {'form': form})

@login_required
@admin_required(login_url='/login/')
def admin_edit_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    if request.method == 'POST':
        form = FolderForm(request.POST, instance=folder)
        if form.is_valid():
            form.save()
            messages.success(request, 'Folder updated successfully.')
            return redirect('custom_admin_dashboard:admin_folders')
    else:
        form = FolderForm(instance=folder)
    return render(request, 'custom_admin_dashboard/admin_edit_folder.html', {'form': form, 'folder': folder})

@login_required
@admin_required(login_url='/login/')
def admin_delete_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    if request.method == 'POST':
        folder.delete()
        messages.success(request, 'Folder deleted successfully.')
        return redirect('custom_admin_dashboard:admin_folders')
    return render(request, 'custom_admin_dashboard/admin_delete_folder.html', {'folder': folder})

@login_required
@admin_required(login_url='/login/')
def admin_documents(request):
    documents = Document.objects.all()
    return render(request, 'custom_admin_dashboard/admin_documents.html', {'documents': documents})

@login_required
@admin_required(login_url='/login/')
def admin_add_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)  # Use request.FILES to handle file uploads
        if form.is_valid():
            form.save()
            messages.success(request, 'Document added successfully.')
            return redirect('custom_admin_dashboard:admin_documents')
    else:
        form = DocumentForm()
    return render(request, 'custom_admin_dashboard/admin_add_document.html', {'form': form})

@login_required
@admin_required(login_url='/login/')
def admin_edit_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)  # Use request.FILES here too
        if form.is_valid():
            form.save()
            messages.success(request, 'Document updated successfully.')
            return redirect('custom_admin_dashboard:admin_documents')
    else:
        form = DocumentForm(instance=document)
    return render(request, 'custom_admin_dashboard/admin_edit_document.html', {'form': form, 'document': document})

@login_required
@admin_required(login_url='/login/')
def admin_delete_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Document deleted successfully.')
        return redirect('custom_admin_dashboard:admin_documents')
    return render(request, 'custom_admin_dashboard/admin_delete_document.html', {'document': document})

# User Management Views
@login_required
@admin_required(login_url='/login/')
def manage_users(request):
    users = User.objects.all()
    return render(request, 'custom_admin_dashboard/admin_manage_user.html', {'users': users})

@login_required
@admin_required(login_url='/login/')
def admin_add_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User added successfully.')
            return redirect('custom_admin_dashboard:manage_users')
    else:
        form = UserForm()
    return render(request, 'custom_admin_dashboard/admin_add_user.html', {'form': form})

@login_required
@admin_required(login_url='/login/')
def admin_edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('custom_admin_dashboard:manage_users')
    else:
        form = UserForm(instance=user)
    return render(request, 'custom_admin_dashboard/admin_edit_user.html', {'form': form, 'user': user})

@login_required
@admin_required(login_url='/login/')
def admin_delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('custom_admin_dashboard:manage_users')
    return render(request, 'custom_admin_dashboard/admin_delete_user.html', {'user': user})
