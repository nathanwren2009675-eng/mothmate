from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import logout

# Simple password gateway
class SitePasswordMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        # Skip password page for these addresses
        if (request.path == '/password/' or 
            request.path.startswith('/static/') or
            request.path.startswith('/admin/') or
            request.path.startswith('/accounts/')):
            return self.get_response(request)
        
        # Check if already passed password
        if request.session.get('site_unlocked'):
            return self.get_response(request)
        
        # Show password page
        return redirect('/password/')

def password_page(request):
    if request.method == 'POST':
        entered = request.POST.get('password', '')
        if entered == settings.SITE_PASSWORD:
            request.session['site_unlocked'] = True
            return redirect('/')
        return render(request, 'password.html', {'error': 'Incorrect password'})
    return render(request, 'password.html')

def login_redirect(request):
    return redirect('/accounts/login/')

def logout_redirect(request):
    logout(request)
    return redirect('/password/')

urlpatterns = [
    path('password/', password_page, name='password_page'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', login_redirect),
    path('logout/', logout_redirect),
    path('', include('records.urls')),  # ✅ Links to ALL your pages
]