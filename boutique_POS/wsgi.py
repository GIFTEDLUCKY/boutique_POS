import os
import sys

# Set correct project directory — this is your actual project root
project_home = '/home/giftedlucky/boutique_POS'

# Add project_home to sys.path
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Activate the virtual environment
activate_this = '/home/giftedlucky/boutique_POS/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boutique_POS.settings')

# Load the Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Optional: Use WhiteNoise to serve static files
from whitenoise import WhiteNoise
application = WhiteNoise(application, root=os.path.join(project_home, 'staticfiles'))
