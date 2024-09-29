# documents/context_processors.py

from .models import Department

def departments_context(request):
    return {
        'departments': Department.objects.all()
    }
