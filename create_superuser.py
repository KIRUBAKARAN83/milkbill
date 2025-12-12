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
    print("Superuser environment variables missing — skipping creation.")
else:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, password=password, email=email)
        print(f"Superuser {username} created.")
    else:
        print(f"Superuser {username} already exists — skipping creation.")
