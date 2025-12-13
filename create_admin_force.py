import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "milkproject.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

USERNAME = "kiruba_karan_123"
PASSWORD = "kiruba@123"

user, created = User.objects.get_or_create(username=USERNAME)

user.set_password(PASSWORD)
user.is_staff = True
user.is_superuser = True
user.save()

print("ADMIN READY | created =", created)
