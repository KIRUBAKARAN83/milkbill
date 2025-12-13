import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "milkproject.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

user = User.objects.get(username="Kiruba_karan_123")  # EXACT username
user.set_password("Kiruba@123")                # SET NEW PASSWORD
user.is_staff = True
user.is_superuser = True
user.save()

print("LOGIN FIXED")
