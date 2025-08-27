from django.urls import path
from . import views

app_name = 'analyzer'

urlpatterns = [
    # Endpoint principal d'analyse
    path('analyze/', views.analyze_website, name='analyze_website'),
    
    # Récupérer une analyse existante
    path('analysis/<str:domain>/', views.get_analysis, name='get_analysis'),
    
    # Lister toutes les analyses
    path('analyses/', views.list_analyses, name='list_analyses'),
    
    # Health check
    path('health/', views.health_check, name='health_check'),
]

