# urls.py
from django.urls import path
from . import views

app_name = 'custom_admin_dashboard'

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.manage_users, name='manage_users'),  # List users
    path('users/add/', views.admin_add_user, name='admin_add_user'),  # Add user
    path('users/edit/<int:user_id>/', views.admin_edit_user, name='admin_edit_user'),  # Edit user
    path('users/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),  # Delete user
    path('departments/', views.admin_departments, name='admin_departments'),
    path('departments/add/', views.admin_add_department, name='admin_add_department'),
    path('departments/edit/<int:department_id>/', views.admin_edit_department, name='admin_edit_department'),
    path('departments/delete/<int:department_id>/', views.admin_delete_department, name='admin_delete_department'),
    path('folders/', views.admin_folders, name='admin_folders'),
    path('folder/<int:folder_id>/', views.admin_open_folder, name='admin_open_folder'),
    path('folders/add/', views.admin_add_folder, name='admin_add_folder'),
    path('folders/edit/<int:folder_id>/', views.admin_edit_folder, name='admin_edit_folder'),
    path('folders/delete/<int:folder_id>/', views.admin_delete_folder, name='admin_delete_folder'),
    path('documents/', views.admin_documents, name='admin_documents'),
    path('documents/<int:document_id>/', views.view_document, name='admin_view_document'),
    path('view_document/<int:document_id>/', views.admin_view_document_content, name='admin_view_document_content'),
    path('documents/add/<int:department_id>/<int:folder_id>/', views.admin_add_document, name='admin_add_document'),
    path('documents/edit/<int:document_id>/', views.admin_edit_document, name='admin_edit_document'),
    path('documents/delete/<int:document_id>/', views.admin_delete_document, name='admin_delete_document'),
    path('departments/view/<int:department_id>/', views.admin_view_department, name='admin_view_department'),
    path('folders/view/<int:folder_id>/', views.admin_view_folder, name='admin_view_folder'),
    path('search/', views.search, name='search'),  # Path for search view
]
