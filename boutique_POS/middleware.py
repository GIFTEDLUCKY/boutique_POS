import datetime
import threading
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from django.shortcuts import redirect

# -----------------------------
# Thread-local user helper
# -----------------------------
_local = threading.local()

def get_current_user():
    return getattr(_local, 'user', None)

# -----------------------------
# License Expiry Middleware
# -----------------------------
class LicenseExpiryMiddleware(MiddlewareMixin):
    """
    Middleware that:
    - Shows color-coded license expiry warnings before expiry.
    - Completely blocks access after the license expires.
    """

    def process_response(self, request, response):
        if not hasattr(response, "content") or "text/html" not in response.get("Content-Type", ""):
            return response

        try:
            expiry_str = getattr(settings, "LICENSE_EXPIRY_DATE", None)
            if not expiry_str:
                return response

            expiry_date = datetime.datetime.strptime(expiry_str, "%Y-%m-%d").date()
            today = datetime.date.today()
            days_left = (expiry_date - today).days

            # If expired → block the site entirely
            if days_left < 0:
                html = f"""
                <html>
                <head><title>License Expired</title></head>
                <body style="
                    background-color:#330000;
                    color:#fff;
                    font-family:Arial, sans-serif;
                    display:flex;
                    flex-direction:column;
                    align-items:center;
                    justify-content:center;
                    height:100vh;
                    text-align:center;
                ">
                    <h1 style="font-size:48px; color:#ff4d4d;">🚫 License Expired</h1>
                    <p style="font-size:20px; max-width:600px;">
                        Your software license expired on 
                        <strong>{expiry_date.strftime('%d %B %Y')}</strong>.
                    </p>
                    <p style="font-size:18px;">
                        Please contact your system administrator or vendor to renew your license.
                    </p>
                </body>
                </html>
                """
                return HttpResponse(html, content_type="text/html")

            # Only show warnings if license still active
            if days_left <= 3:
                message = f"⚠️ License will expire in {days_left} day(s)!"
                color = "#ff4d4d"
            elif days_left <= 7:
                message = f"⚠️ License will expire in {days_left} day(s)!"
                color = "#ff944d"
            elif days_left <= 14:
                message = f"⚠️ License will expire in {days_left} day(s)!"
                color = "#ffd633"
            elif days_left <= 21:
                message = f"⚠️ License will expire in {days_left} day(s)!"
                color = "#ffff66"
            else:
                return response  # no message if more than 3 weeks left

            # Floating notice
            notice_html = f"""
            <div id="license-notice" style="
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                background-color: {color};
                color: #000;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                z-index: 9999;
                text-align: center;
            ">
                {message}
                <span onclick="document.getElementById('license-notice').style.display='none';"
                      style="cursor:pointer; margin-left:20px; font-weight:bold;">&times;</span>
            </div>
            """

            # Inject notice into HTML
            content = response.content.decode("utf-8")
            if "<body" in content:
                response.content = content.replace("<body>", f"<body>{notice_html}", 1).encode("utf-8")

        except Exception:
            pass

        return response
    

    
# -----------------------------
# Login Required Middleware
# -----------------------------
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

class LoginRequiredMiddleware(MiddlewareMixin):
    """
    Restricts access to all views unless user is authenticated.
    Redirects to 'accounts/login' when session expires or user is not logged in.
    """

    PUBLIC_PATHS = [
        '/accounts/login/',
        '/accounts/signup/',
        '/accounts/register/',
        '/accounts/password_reset/',
        '/accounts/reset/',
        '/accounts/logout/',
        '/admin/',
        '/goodbye/',
    ]

    def process_request(self, request):
        # Allow static and media files so assets load on login page
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return None

        # Allow whitelisted (public) URLs
        if any(request.path.startswith(path) for path in self.PUBLIC_PATHS):
            return None

        # If not authenticated → redirect to accounts/login
        if not request.user.is_authenticated:
            try:
                login_url = reverse('accounts/login')
            except Exception:
                # fallback to path if name not found
                login_url = '/accounts/login/'
            return redirect(login_url)

        return None

