from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Department, Folder, Document, Profile, VerificationCode  
from .forms import DocumentForm, FolderForm, RegistrationForm, LoginForm, ProfileCompletionForm, VerificationForm
from datetime import date
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
import base64
import random
import os
from django.conf import settings
from .forms import RegistrationForm
from django.http import HttpResponse




def generate_username(email):
    username_base = email.split('@')[0]
    username = username_base
    counter = 1
    while User.objects.filter(username=username).exists():  # Use default User model
        username = f"{username_base}{counter}"
        counter += 1
    return username


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User is inactive until email verification
            user.username = generate_username(user.email)
            user.save()  # Save user to the database

            # Store user ID in session for email verification flow
            request.session['user_id'] = user.id
            messages.success(request, "Registration successful. A verification code has been sent to your email.")
            return redirect('documents:verify_email')
        else:
            # Display form errors in case of invalid form submission
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})

def send_verification_code(user):
    code = random.randint(1000, 9999)
    verification_code = VerificationCode(
        user=user,
        code=str(code),
        expires_at=timezone.now() + timedelta(minutes=1)  # Set expiration time to 1 minute from now
    )
    verification_code.save()

    send_mail(
        'Your Verification Code',
        f"Your username is {user.username}.\nYour verification code is {code}. Please note that this code will expire in 1 minute.",
        'from@example.com',
        [user.email],
        fail_silently=False,
    )

def resend_verification_code(request):
    user_id = request.session.get('user_id')
    if user_id:
        user = get_object_or_404(User, id=user_id)  # Use default User model
        send_verification_code(user)  # Call without first_name
        messages.success(request, "Verification code has been resent to your email.")
    else:
        messages.error(request, "Could not resend verification code. Please try again.")
    return redirect('documents:verify_email')


def verify_email(request):
    if request.method == 'POST':
        form = VerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            user_id = request.session.get('user_id')
            if user_id:
                user = get_object_or_404(User, id=user_id)
                verification_code = user.verification_codes.filter(code=code, used=False).first()
                if verification_code and not verification_code.is_expired():
                    verification_code.used = True
                    verification_code.save()

                    # Send email notifying the user that the account is under review
                    send_mail(
                        'Email Verified - Awaiting Account Approval',
                        f'Hello {user.username},\n\nThank you for verifying your email. Your registration is now under review by the admin team. You will be notified once your account is approved.\n\nBest regards,\nYour Team',
                        settings.EMAIL_HOST_USER,
                        [user.email],
                        fail_silently=False,
                    )

                    messages.success(request, "Email verified successfully. Your account is now under review.")
                    return redirect('documents:login')
                else:
                    messages.error(request, "Invalid or expired verification code.")
    else:
        form = VerificationForm()
    return render(request, 'verify_email.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(email=username_or_email) if '@' in username_or_email else User.objects.get(username=username_or_email)  # Use default User model
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    if not user.is_active:
                        messages.error(request, "Your account is not active. Please check your email for verification instructions.")
                    else:
                        login(request, user)
                        if user.is_superuser:
                            return redirect('custom_admin_dashboard:admin_dashboard')  # Redirect to admin dashboard
                        else:
                            profile = Profile.objects.get(user=user)
                            if profile.is_profile_complete:
                                return redirect('documents:home')  # Redirect to documents home
                            else:
                                return redirect('documents:complete_profile')  # Redirect to profile completion page
                else:
                    messages.error(request, "Invalid username or password.")
            except User.DoesNotExist:  # Use default User model
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def get_profile_data(user):
    try:
        profile = Profile.objects.get(user=user)
        profile_image_base64 = None
        if profile.profile_image:
            profile_image_base64 = base64.b64encode(profile.profile_image).decode('utf-8')
        department_name = profile.department.name if profile.department else "N/A"
        return {
            'profile_image_base64': profile_image_base64,
            'department_name': department_name
        }
    except Profile.DoesNotExist:
        return {
            'profile_image_base64': None,
            'department_name': "N/A"
        }

@login_required
def complete_profile(request):
    profile_data = get_profile_data(request.user)
    
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('documents:home')

    if request.method == 'POST':
        form = ProfileCompletionForm(request.POST, instance=profile)
        uploaded_file = request.FILES.get('profile_image')

        if form.is_valid():
            profile = form.save(commit=False)
            if uploaded_file:
                profile.profile_image = uploaded_file.read()
            profile.is_profile_complete = all([
                profile.nationalID,
                profile.contact_number,
                profile.department,
                profile.profile_image
            ])
            profile.save()
            messages.success(request, "Your profile has been successfully completed!")
            return redirect('documents:home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileCompletionForm(instance=profile)

    # profile_completion_percentage = profile.completion_percentage()

    context = {
        'form': form,
        # 'profile_completion_percentage': profile_completion_percentage,
    }
    context.update(profile_data)

    return render(request, 'documents/complete_profile.html', context)

@login_required
def home(request):
    profile_data = get_profile_data(request.user)

    try:
        profile = Profile.objects.get(user=request.user)
        user_department = profile.department
    except Profile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('documents:complete_profile')

    user_department_name = user_department.name if user_department else "N/A"

    context = {
        'profile_data': profile,
        'user_department_name': user_department_name,
    }
    context.update(profile_data)

    return render(request, 'documents/documents_dashboard.html', context)

@login_required
def search(request):
    profile_data = get_profile_data(request.user)
    query = request.GET.get('q')
    departments = Department.objects.filter(name__icontains=query) if query else Department.objects.none()
    folders = Folder.objects.filter(name__icontains=query) if query else Folder.objects.none()
    documents = Document.objects.filter(file_name__icontains=query) if query else Document.objects.none()

    context = {
        'query': query,
        'departments': departments,
        'folders': folders,
        'documents': documents,
    }
    context.update(profile_data)

    return render(request, 'documents/search_results.html', context)

@login_required
def view_document_content(request, document_id):
    profile_data = get_profile_data(request.user)
    document = get_object_or_404(Document, id=document_id)
    file_content = base64.b64decode(document.file_content)
    content_type = 'application/octet-stream'
    is_pdf = document.file_extension == '.pdf'
    is_image = document.file_extension in ['.jpg', '.jpeg', '.png']
    is_docx = document.file_extension == '.docx'

    base64_file_content = base64.b64encode(file_content).decode('utf-8')

    context = {
        'document': document,
        'file_content': base64_file_content,
        'content_type': content_type,
        'is_pdf': is_pdf,
        'is_image': is_image,
        'is_docx': is_docx,
    }
    context.update(profile_data)

    return render(request, 'documents/document_content.html', context)

@login_required
def upload_document(request, department_id=None, folder_id=None):
    profile_data = get_profile_data(request.user)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            uploaded_file = request.FILES.get('file_content')

            if uploaded_file:
                document.file_content = base64.b64encode(uploaded_file.read())
                document.created_by = request.user
                document.file_extension = os.path.splitext(uploaded_file.name)[1]

                if folder_id:
                    folder = get_object_or_404(Folder, id=folder_id)
                    document.folder = folder
                else:
                    department = get_object_or_404(Department, id=department_id)
                    folder_name = date.today().strftime('%Y-%m-%d')
                    folder, created = Folder.objects.get_or_create(name=folder_name, department=department)
                    document.folder = folder

                document.save()
                messages.success(request, 'Document uploaded successfully.')
                return redirect('documents:folder_detail', department_id=department_id, folder_id=folder.id)

            else:
                messages.error(request, 'No file uploaded.')
        else:
            messages.error(request, 'Form is not valid.')
    else:
        form = DocumentForm()

    context = {
        'form': form,
    }
    context.update(profile_data)

    return render(request, 'documents/upload_document.html', context)

@login_required
def create_folder(request):
    profile_data = get_profile_data(request.user)
    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.created_by = request.user
            folder.department = request.user.profile.department
            folder.save()
            return redirect('documents:department_detail', department_id=folder.department.id)
    else:
        form = FolderForm()

    context = {
        'form': form,
    }
    context.update(profile_data)

    return render(request, 'documents/create_folder.html', context)

@login_required
def folder_detail(request,department_id, folder_id):
    profile_data = get_profile_data(request.user)
    folder = get_object_or_404(Folder, id=folder_id)
    documents = Document.objects.filter(folder=folder)

    context = {
        'documents': documents,
        'folder': folder,
        'department_id': department_id,
    }
    context.update(profile_data)

    return render(request, 'documents/document_list.html', context)

@login_required
def department_detail(request, department_id):
    profile_data = get_profile_data(request.user)
    department = get_object_or_404(Department, id=department_id)
    folders = department.folders.all()
    documents = Document.objects.filter(folder__department=department)

    context = {
        'department': department,
        'folders': folders,
        'documents': documents,
    }
    context.update(profile_data)

    return render(request, 'documents/department_details.html', context)

def user_logout(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('documents:login')
