from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from documents.models import Department, Folder, Document, Profile
from documents.forms import ProfileCompletionForm
from django.contrib.auth.models import User
from .forms import DepartmentForm, FolderForm, DocumentForm, RegistrationForm, EditUserForm
from django.db.models import Q
from django.http import HttpResponse
import base64
import os
import random
import string
from django.core.mail import send_mail,BadHeaderError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse  # Import reverse for URL generation

CustomUser = get_user_model()


def serve_profile_image(request, user_id):
    # Fetch the user's profile
    profile = get_object_or_404(Profile, user_id=user_id)
    
    # Check if the profile_image field has data
    if profile.profile_image:
        # Return the image as an HttpResponse with appropriate content type
        return HttpResponse(profile.profile_image, content_type="image/jpeg")  # Adjust the content type if necessary
    else:
        # Handle the case where there is no profile image
        return HttpResponse(status=404)  # Or you could return a default image here if preferred

def admin_required(login_url=None):
    return user_passes_test(lambda u: u.is_superuser, login_url=login_url)

@login_required
@admin_required(login_url='/login/')
def admin_dashboard(request):
    try:
        profile = Profile.objects.get(user=request.user)  # Get the user's profile
    except Profile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('custom_admin_dashboard:admin_dashboard')  # Adjust this redirect as necessary

    # Calculate the profile completion percentage
    profile_completion_percentage = profile.completion_percentage()  # Use the model method

    # Render the dashboard template with the profile completion percentage
    return render(request, 'custom_admin_dashboard/admin_dashboard.html', {
        'profile_completion_percentage': profile_completion_percentage,
        # Include other context variables as needed
    })


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


    context = {
        'query': query,
        'departments': departments,  # Pass actual department objects
        'folders': folders,          # Pass actual folder objects
        'documents': documents,      # Pass actual document objects
        'total_results': total_results,
    }
    
    return render(request, 'custom_admin_dashboard/search_results.html', context)


@login_required
@admin_required(login_url='/login/')
def admin_complete_profile(request):
    try:
        profile = Profile.objects.get(user=request.user)  # Get the user's profile
    except Profile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('custom_admin_dashboard:admin_dashboard')  # Redirect to admin dashboard if profile doesn't exist

    if request.method == 'POST':
        form = ProfileCompletionForm(request.POST, instance=profile)  # Use the form for other fields
        uploaded_file = request.FILES.get('profile_image')  # Get the uploaded file

        if form.is_valid():
            profile = form.save(commit=False)  # Save form data without committing to the database
            
            # Convert the uploaded image to binary format and save it
            if uploaded_file:
                document_data = uploaded_file.read()  # Read the uploaded file into memory
                profile.profile_image = document_data  # Save the binary data directly
            
            # Check if all required fields are filled before marking profile as complete
            all_fields_filled = all([
                profile.nationalID,
                profile.contact_number,
                profile.department,
                profile.profile_image,  # Ensure the image is uploaded
            ])
            profile.is_profile_complete = all_fields_filled  # Update the completion status
            
            profile.save()  # Save the profile
            messages.success(request, "Your profile has been successfully completed!")
            return redirect('custom_admin_dashboard:admin_dashboard')  # Redirect to the admin dashboard after completion
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = ProfileCompletionForm(instance=profile)  # Pre-fill the form with existing profile data

    # Calculate the profile completion percentage using the model method
    profile_completion_percentage = profile.completion_percentage()

    return render(request, 'custom_admin_dashboard/complete_profile.html', {
        'form': form,
        'profile_completion_percentage': profile_completion_percentage,
    })

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


# folder management

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
        form = DocumentForm(request.POST, request.FILES)  # Include request.FILES here
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


# manage users

@login_required
@admin_required(login_url='/login/')
def manage_users(request):
    users = User.objects.all()  # Change this to CustomUser
    return render(request, 'custom_admin_dashboard/admin_manage_user.html', {'users': users})


@login_required
@admin_required(login_url='/login/')
def admin_pending_users(request):
    # Fetch users that are inactive (pending activation)
    pending_users = User.objects.filter(is_active=False)
    departments = Department.objects.all()  # Fetch all departments

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        department_id = request.POST.get('department_id')

        user = get_object_or_404(User, id=user_id)

        if action == 'activate':
            # Fetch or create the user's profile if it doesn't exist
            profile, created = Profile.objects.get_or_create(user=user)

            if department_id:
                department = get_object_or_404(Department, id=department_id)
                profile.department = department  # Assign the department to the profile
            
            user.is_active = True
            user.save()  # Activate the user
            profile.save()  # Save the profile with updated department if provided

            # Generate the login URL
            login_url = request.build_absolute_uri(reverse('documents:login'))  # Update this to match your login URL name

            # Send activation email
            send_mail(
                'Your Account Has Been Activated',
                f'Hello {user.username},\n\nYour account has been activated and you have been assigned to the {profile.department.name if profile.department else "No department"} department.\n\n'
                f'You can log in using the following link:\n{login_url}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

            messages.success(request, f"{user.username} has been activated and assigned to {profile.department.name if profile.department else 'No department'}.")
        
        elif action == 'deny':
            # Send denial email
            send_mail(
                'Your Account Registration Has Been Denied',
                f'Hello {user.username},\n\nUnfortunately, your account registration has been denied.',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            user.delete()  # Alternatively, you could set a flag instead of deleting
            messages.warning(request, f"{user.username}'s registration has been denied.")
        
        return redirect('custom_admin_dashboard:admin_pending_users')

    return render(request, 'custom_admin_dashboard/admin_pending_users.html', {
        'pending_users': pending_users,
        'departments': departments,  # Pass departments to the template
    })



@login_required
@admin_required(login_url='/login/')
def admin_add_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            department = form.cleaned_data.get("department")
            username = email.split('@')[0]
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

            # Check if user already exists
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "A user with this email already exists.")
                return render(request, 'custom_admin_dashboard/admin_add_user.html', {'form': form})
            
            # Create the user
            user = CustomUser.objects.create_user(username=username, email=email, password=password)

            try:
                # Check for existing profile or create a new one
                profile, created = Profile.objects.get_or_create(user=user, defaults={'department': department})
                if not created:
                    # If a profile already existed, update the department if needed
                    profile.department = department
                    profile.save()

                # Prepare email content
                subject = "Your New Account Information"
                message = (
                    f"Hello,\n\nAn account has been created for you.\n\n"
                    f"Username: {username}\nPassword: {password}\n\n"
                    "Please log in and change your password after your first login."
                )

                # Send email with login credentials
                send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)
                messages.success(request, 'User added successfully, and email sent with login credentials.')
            except (BadHeaderError, Exception) as e:
                # Clean up if there's an error
                user.delete()  # Clean up the user if profile creation or email fails
                messages.error(request, f"An error occurred: {str(e)}")
                return render(request, 'custom_admin_dashboard/admin_add_user.html', {'form': form})

            return redirect('custom_admin_dashboard:manage_users')

    else:
        form = RegistrationForm()

    return render(request, 'custom_admin_dashboard/admin_add_user.html', {'form': form})

@login_required
@admin_required(login_url='/login/')
def admin_edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)  # Fetch the user
    profile = get_object_or_404(Profile, user=user)  # Fetch the associated profile

    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user)  # Create form instance with user data
        if form.is_valid():
            updated_user = form.save()  # Save the user first
            
            # Update the profile department if changed
            new_department_id = request.POST.get('department')  # Get the new department from POST data
            if new_department_id:
                profile.department_id = new_department_id  # Update the profile's department
            
            profile.save()  # Save the profile changes
            
            messages.success(request, 'User updated successfully.')  # Success message
            return redirect('custom_admin_dashboard:manage_users')  # Redirect to manage users

    else:
        form = EditUserForm(instance=user)  # Create form instance for GET request

    return render(request, 'custom_admin_dashboard/admin_edit_user.html', {'form': form, 'user': user, 'profile': profile})




@login_required
@admin_required(login_url='/login/')
def admin_delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)  # Change this to CustomUser
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('custom_admin_dashboard:manage_users')
    return render(request, 'custom_admin_dashboard/admin_delete_user.html', {'user': user})


