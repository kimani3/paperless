# documents/context_processors.py

from .models import Department

def departments_context(request):
    user_department = None
    if request.user.is_authenticated:
        user_department = request.user.department  # Assuming User model has a 'department' field
    return {
        'user_department': user_department
    }
