# documents/admin.py
from django.contrib import admin
from .models import Department, Folder, Document

class DocumentAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'created_by', 'updated_at')

class FolderAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'created_by', 'updated_at')

class DepartmentAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'created_by', 'updated_at')

admin.site.register(Department, DepartmentAdmin)
admin.site.register(Folder, FolderAdmin)
admin.site.register(Document, DocumentAdmin)
