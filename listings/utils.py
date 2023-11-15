# utils.py within your app directory

from .models import Technology

def get_corresponding_technologies(skill):
    # Replace the following line with your actual logic
    return Technology.objects.filter(name__icontains=skill.name)
