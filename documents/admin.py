from django.contrib import admin
from .models import Department, Folder, Document, Profile

class DocumentAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'created_by', 'updated_at')
    list_display = ('file_name', 'folder', 'created_at', 'created_by')  # Display relevant fields in the list view
    search_fields = ('file_name',)  # Enable searching by file name

class FolderAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'created_by', 'updated_at')
    list_display = ('name', 'department', 'created_at')  # Display relevant fields in the list view
    search_fields = ('name',)  # Enable searching by folder name

class DepartmentAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'created_by', 'updated_at')
    list_display = ('name', 'created_at')  # Display relevant fields in the list view
    search_fields = ('name',)  # Enable searching by department name

class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'created_by')
    list_display = ('user', 'nationalID', 'contact_number', 'is_profile_complete')  # Display relevant fields in the list view
    search_fields = ('user__username', 'nationalID')  # Enable searching by user or national ID

# Register your models with the corresponding admin classes
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Folder, FolderAdmin)
admin.site.register(Document, DocumentAdmin)
