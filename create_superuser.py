import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "milkproject.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")

if not username or not password:
    print("Missing env vars")
else:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": email}
    )

    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()

    if created:
        print("Superuser created")
    else:
        print("Superuser password updated")
