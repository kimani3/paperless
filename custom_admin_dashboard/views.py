from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from documents.models import Department, Folder, Document, CustomUser
from django.contrib.auth.models import User
from .forms import DepartmentForm, FolderForm, DocumentForm, RegistrationForm
from django.db.models import Q
from django.http import HttpResponse
import base64
import os
from datetime import date

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

def highlight_query(text, query):
    if query:
        highlighted_text = text.replace(query, f'<span class="highlight">{query}</span>')
        return highlighted_text
    return text

@login_required
@admin_required(login_url='/login/')
def search(request):
    query = request.GET.get('q')
    
    # Filter results based on the query
    departments = Department.objects.filter(name__icontains=query) if query else Department.objects.none()
    folders = Folder.objects.filter(name__icontains=query) if query else Folder.objects.none()
    documents = Document.objects.filter(file_name__icontains=query) if query else Document.objects.none()
    
    # Count total results
    total_results = departments.count() + folders.count() + documents.count()

    # Highlight matching text
    highlighted_departments = [highlight_query(department.name, query) for department in departments]
    highlighted_folders = [highlight_query(folder.name, query) for folder in folders]
    highlighted_documents = [highlight_query(document.file_name, query) for document in documents]

    context = {
        'query': query,
        'departments': departments,  # Pass actual department objects
        'folders': folders,          # Pass actual folder objects
        'documents': documents,      # Pass actual document objects
        'highlighted_departments': highlighted_departments,
        'highlighted_folders': highlighted_folders,
        'highlighted_documents': highlighted_documents,
        'total_results': total_results,
    }
    
    return render(request, 'custom_admin_dashboard/search_results.html', context)


# departrment management
@login_required
@admin_required(login_url='/login/')
def admin_view_department(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    folders = department.folders.all()  # Fetch all folders related to the department
    return render(request, 'custom_admin_dashboard/admin_view_folder.html', {
        'department': department,
        'folders': folders,  # Pass the folders to the template
    })

@login_required
@admin_required(login_url='/login/')
def admin_open_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    documents = folder.documents.all()  # Fetch all documents related to the folder
    return render(request, 'custom_admin_dashboard/admin_view_document.html', {
        'folder': folder,
        'documents': documents,  # Pass the documents to the template
    })


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
def admin_view_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    
    # Ensure the folder has an associated department
    if folder.department is None:
        messages.error(request, 'This folder does not belong to any department.')
        return redirect('custom_admin_dashboard:admin_folders')  # Redirect to the folder list or any relevant page
    
    documents = folder.documents.all()  # Fetch documents related to the folder
    department_id = folder.department.id  # Get the department ID
    return render(request, 'custom_admin_dashboard/admin_view_document.html', {
        'folder': folder,
        'documents': documents,
        'department_id': department_id,  # Pass department ID to the template
    })



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

# document management
@login_required
@admin_required(login_url='/login/')
def admin_documents(request):
    documents = Document.objects.all()
    return render(request, 'custom_admin_dashboard/admin_documents.html', {'documents': documents})

@login_required
@admin_required(login_url='/login/')
def admin_add_document(request, department_id=None, folder_id=None):
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

                folder = get_object_or_404(Folder, id=folder_id)
                document.folder = folder  # Assign folder

                # Save the document instance
                document.save()
                messages.success(request, 'Document uploaded successfully.')
                return redirect('custom_admin_dashboard:admin_view_folder', folder.id)
            else:
                messages.error(request, 'No file uploaded.')
        else:
            messages.error(request, 'Form is not valid.')
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

@login_required
def view_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    response = HttpResponse(document.file_content, content_type='application/octet-stream')
    response['Content-Disposition'] = f'inline; filename="{document.file_name}"'
    return response

@login_required
def admin_view_document_content(request, document_id):
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

    return render(request, 'custom_admin_dashboard/admin_document_content.html', {
        'document': document,
        'file_content': base64_file_content,
        'content_type': content_type,
        'is_pdf': is_pdf,
        'is_image': is_image,
        'is_docx': is_docx,
    })


@login_required
@admin_required(login_url='/login/')
def manage_users(request):
    users = CustomUser.objects.all()  # Change this to CustomUser
    return render(request, 'custom_admin_dashboard/admin_manage_user.html', {'users': users})

@login_required
@admin_required(login_url='/login/')
def admin_add_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)  # Use your RegistrationForm
        if form.is_valid():
            form.save()
            messages.success(request, 'User added successfully.')
            return redirect('custom_admin_dashboard:manage_users')
    else:
        form = RegistrationForm()
    return render(request, 'custom_admin_dashboard/admin_add_user.html', {'form': form})

@login_required
@admin_required(login_url='/login/')
def admin_edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)  # Change this to CustomUser
    if request.method == 'POST':
        form = RegistrationForm(request.POST, instance=user)  # Use your RegistrationForm
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('custom_admin_dashboard:manage_users')
    else:
        form = RegistrationForm(instance=user)
    return render(request, 'custom_admin_dashboard/admin_edit_user.html', {'form': form, 'user': user})



@login_required
@admin_required(login_url='/login/')
def admin_delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)  # Change this to CustomUser
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('custom_admin_dashboard:manage_users')
    return render(request, 'custom_admin_dashboard/admin_delete_user.html', {'user': user})

# folder management
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
