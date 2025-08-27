from rest_framework import serializers
from .models import WebsiteAnalysis, LegalDocument


class LegalDocumentSerializer(serializers.ModelSerializer):
    """Serializer pour les documents juridiques"""
    
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    
    class Meta:
        model = LegalDocument
        fields = [
            'id',
            'document_type',
            'document_type_display',
            'url',
            'title',
            'content_length',
            'extracted_at'
        ]


class WebsiteAnalysisSerializer(serializers.ModelSerializer):
    """Serializer pour les analyses de sites web"""
    
    documents = LegalDocumentSerializer(many=True, read_only=True)
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    
    class Meta:
        model = WebsiteAnalysis
        fields = [
            'id',
            'domain',
            'url',
            'summary',
            'key_points',
            'what_you_accept',
            'data_collected',
            'data_usage',
            'data_sharing',
            'retention_period',
            'critical_points',
            'readability_score',
            'risk_level',
            'risk_level_display',
            'created_at',
            'updated_at',
            'documents_found',
            'documents',
            'is_successful',
            'error_message'
        ]


class AnalyzeRequestSerializer(serializers.Serializer):
    """Serializer pour les requêtes d'analyse"""
    
    url = serializers.URLField(
        help_text="URL du site web à analyser (ex: https://example.com)"
    )
    
    def validate_url(self, value):
        """Validation de l'URL"""
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError(
                "L'URL doit commencer par http:// ou https://"
            )
        return value


class AnalyzeResponseSerializer(serializers.Serializer):
    """Serializer pour les réponses d'analyse"""
    
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = WebsiteAnalysisSerializer(required=False)
    error = serializers.CharField(required=False)

