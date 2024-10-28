# documents/context_processors.py

from django.conf import settings
from .models import Profile

def departments_context(request):
    user_department = None
    if request.user.is_authenticated:
        try:
            user_department = request.user.profile.department  # Accessing department via Profile
        except Profile.DoesNotExist:
            user_department = None  # Handle case where Profile doesn't exist
    return {
        'user_department': user_department,
        # Add any other context variables you need
    }
