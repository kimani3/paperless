# custom_admin_dashboard/context_processors.py

from django.contrib.auth.models import User
from documents.models import Profile
import base64

def profile_image(request):
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
            profile_image = profile.profile_image  # Get the profile image
            profile_image_url = None
            
            # Convert binary image data to base64
            if isinstance(profile_image, bytes):
                profile_image_url = f"data:image/jpeg;base64,{base64.b64encode(profile_image).decode('utf-8')}"
                
            return {
                'profile_image': profile_image_url,  # Add the profile image to the context
            }
        except Profile.DoesNotExist:
            return {'profile_image': None}  # Profile does not exist, return None
    return {'profile_image': None}  # User is not authenticated
