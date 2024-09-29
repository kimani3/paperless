from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('accounts/login/', views.user_login, name='login'),
    path('accounts/logout/', views.user_logout, name='logout'),
    path('upload/', views.upload_document, name='upload_document'),
    path('manage_department/', views.manage_department, name='manage_department'),
    path('create_folder/', views.create_folder, name='create_folder'),
    path('documents/', views.document_list, name='document_list'),
    path('folders/', views.folder_list, name='folder_list'),
    path('folders/<int:folder_id>/', views.folder_detail, name='folder_detail'),
    path('documents/<int:document_id>/', views.view_document, name='view_document'),
    path('departments/', views.department_list, name='department_list'),
    path('departments/<int:department_id>/', views.department_detail, name='department_detail'),  # New path for detail view
]

