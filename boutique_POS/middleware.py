from django.conf import settings
from datetime import datetime
from django.http import HttpResponse

class ExpiryCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_date = datetime.now()

        if current_date >= settings.EXPIRATION_DATE:
            return HttpResponse(
                """
                <html>
                <head>
                    <style>
                        body {
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            text-align: center;
                            font-family: Arial, sans-serif;
                        }
                    </style>
                </head>
                <body>
                    <div>
                        <h1>Product License Expired</h1>
                        <p>This product has expired and it's temporarily deactivated.</p>
                        <p>Please Contact GLIMS Inventory for Assistance.</p>
                    </div>
                </body>
                </html>
                """,
                content_type="text/html"
            )

        return self.get_response(request)


# middleware.py
import threading

_local = threading.local()

def get_current_user():
    return getattr(_local, 'user', None)

# middleware.py

class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ensure user is authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            _local.user = request.user  # Store the user in thread-local storage
        else:
            _local.user = None  # No user logged in
        response = self.get_response(request)
        return response

