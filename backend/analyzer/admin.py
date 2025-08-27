from django.contrib import admin
from .models import WebsiteAnalysis, LegalDocument


@admin.register(WebsiteAnalysis)
class WebsiteAnalysisAdmin(admin.ModelAdmin):
    """Administration des analyses de sites web"""
    
    list_display = [
        'domain', 
        'risk_level', 
        'readability_score', 
        'is_successful',
        'created_at'
    ]
    
    list_filter = [
        'risk_level',
        'is_successful',
        'created_at',
        'readability_score'
    ]
    
    search_fields = ['domain', 'url']
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('domain', 'url', 'is_successful', 'error_message')
        }),
        ('Résultats de l\'analyse', {
            'fields': (
                'summary',
                'what_you_accept',
                'data_collected', 
                'data_usage',
                'data_sharing',
                'retention_period',
                'critical_points'
            )
        }),
        ('Scores et évaluation', {
            'fields': ('readability_score', 'risk_level', 'key_points')
        }),
        ('Métadonnées', {
            'fields': ('documents_found', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('documents')


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    """Administration des documents juridiques"""
    
    list_display = [
        'analysis',
        'document_type',
        'title',
        'content_length',
        'extracted_at'
    ]
    
    list_filter = [
        'document_type',
        'extracted_at'
    ]
    
    search_fields = [
        'analysis__domain',
        'title',
        'url'
    ]
    
    readonly_fields = ['content_length', 'extracted_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('analysis', 'document_type', 'url', 'title')
        }),
        ('Contenu', {
            'fields': ('content', 'content_length'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('extracted_at',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('analysis')


# Configuration du site admin
admin.site.site_header = "Legal Document Analyzer - Administration"
admin.site.site_title = "Legal Analyzer Admin"
admin.site.index_title = "Gestion des analyses juridiques"

