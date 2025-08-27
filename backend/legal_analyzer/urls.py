"""
URL configuration for legal_analyzer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    """Vue racine de l'API"""
    return JsonResponse({
        'message': 'API Legal Document Analyzer',
        'version': '1.0.0',
        'endpoints': {
            'analyze': '/api/analyze/',
            'analysis': '/api/analysis/{domain}/',
            'analyses': '/api/analyses/',
            'health': '/api/health/',
            'admin': '/admin/'
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('analyzer.urls')),
    path('', api_root, name='api_root'),
]

