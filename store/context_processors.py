from .models import Tag

def tags_processor(request):
    """
    Returns the list of all tags to be available globally in templates.
    Used for the sidebar navigation.
    """
    return {
        'tags': Tag.objects.all()
    }
