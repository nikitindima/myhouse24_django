from django.contrib.auth import get_user_model
from config import celery_app

User = get_user_model()


@celery_app.task()
def get_users_count():
    """Make a pointless Celery task to demonstrate usage."""
    return User.objects.count()
