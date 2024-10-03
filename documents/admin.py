# documents/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Department, Folder, Document,CustomUser

class DocumentAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'created_by', 'updated_at')

class FolderAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'created_by', 'updated_at')

class DepartmentAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'created_by', 'updated_at')

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('department',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Folder, FolderAdmin)
admin.site.register(Document, DocumentAdmin)
