# documents/urls.py
from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('verify_email/', views.verify_email, name='verify_email'),
    path('accounts/login/', views.user_login, name='login'),
    path('accounts/logout/', views.user_logout, name='logout'),
    path('upload/<int:department_id>/<int:folder_id>/', views.upload_document, name='upload_document'),  # Updated URL
    path('create_folder/', views.create_folder, name='create_folder'),
    path('folders/<int:folder_id>/', views.folder_detail, name='folder_detail'),
    path('view_document/<int:document_id>/', views.view_document_content, name='view_document_content'),  # New URL
    path('departments/<int:department_id>/', views.department_detail, name='department_detail'),
    path('search/', views.search, name='search'),
    
    # Add profile completion URLs
    path('complete_profile/step1/', views.complete_profile_step1, name='complete_profile_step1'),
    path('complete_profile/step2/', views.complete_profile_step2, name='complete_profile_step2'),
]
