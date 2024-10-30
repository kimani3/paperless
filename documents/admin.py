from django.contrib import admin
from .models import Department, Folder, Document, Profile

class DocumentAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'created_by', 'updated_at')
    list_display = ('file_name', 'folder', 'created_at', 'created_by')
    search_fields = ('file_name',)

class FolderAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'created_by', 'updated_at')
    list_display = ('name', 'department', 'created_at')
    search_fields = ('name',)

class DepartmentAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'created_by', 'updated_at')
    list_display = ('name', 'created_at')
    search_fields = ('name',)

class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)  # Use a list or tuple here
    list_display = ('user', 'nationalID', 'contact_number', 'is_profile_complete')
    search_fields = ('user__username', 'nationalID')

# Register your models with the corresponding admin classes
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Folder, FolderAdmin)
admin.site.register(Document, DocumentAdmin)
