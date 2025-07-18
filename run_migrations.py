 
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "multi_store_pos.settings")  # Replace with your actual project name
django.setup()

from django.core.management import call_command
call_command("migrate")
