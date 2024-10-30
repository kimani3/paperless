# documents/context_processors.py

from django.contrib.auth.models import User
from .models import Profile
import base64

def user_profile_context(request):
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
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
    return {}
