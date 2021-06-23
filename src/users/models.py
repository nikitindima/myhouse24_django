from django.contrib.auth.models import AbstractUser
from django.urls import reverse


class User(AbstractUser):
    first_name = None
    last_name = None

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
