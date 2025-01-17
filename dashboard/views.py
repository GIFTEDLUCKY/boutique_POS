from django.shortcuts import render
from store.models import Store
from accounts.decorators import role_required

@role_required(['admin'])
def index(request):
    stores = Store.objects.all()
    return render(request, 'dashboard/index.html', {'stores': stores})  # Render the index template
