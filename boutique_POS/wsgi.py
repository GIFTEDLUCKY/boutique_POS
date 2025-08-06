import os
import sys

# Add your project directory to the sys.path
project_home = '/home/giftedlucky/boutique_POS'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Activate your virtual environment
activate_this = '/home/giftedlucky/boutique_POS/venv/bin/activate_this.py'
with open(activate_this) as f:
    exec(f.read(), dict(__file__=activate_this))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boutique_POS.settings')

# Get WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Optional: Static files (if using WhiteNoise)
from whitenoise import WhiteNoise
application = WhiteNoise(application, root=os.path.join(project_home, 'staticfiles'))
