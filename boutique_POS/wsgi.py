import os
import sys

# Set project base directory
project_home = '/home/giftedlucky/boutique_POS'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boutique_POS.settings')

# Set up Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Optional: Enable WhiteNoise for static files
from whitenoise import WhiteNoise
application = WhiteNoise(application, root=os.path.join(project_home, 'staticfiles'))
