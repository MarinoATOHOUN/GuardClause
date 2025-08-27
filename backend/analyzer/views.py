from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from urllib.parse import urlparse
import logging

from .models import WebsiteAnalysis, LegalDocument
from .serializers import (
    AnalyzeRequestSerializer, 
    AnalyzeResponseSerializer,
    WebsiteAnalysisSerializer
)
from .document_extractor import DocumentExtractor
from .llm_utils import analyze_legal_documents

logger = logging.getLogger(__name__)


@api_view(['POST'])
def analyze_website(request):
    """
    API endpoint pour analyser un site web
    
    POST /api/analyze/
    {
        "url": "https://example.com"
    }
    """
    
    # Validation des données d'entrée
    serializer = AnalyzeRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'success': False,
            'message': 'Données invalides',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    url = serializer.validated_data['url']
    
    try:
        # Extraire le domaine
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Vérifier si l'analyse existe déjà (moins de 24h)
        existing_analysis = WebsiteAnalysis.objects.filter(
            domain=domain,
            created_at__gte=timezone.now() - timezone.timedelta(hours=24),
            is_successful=True
        ).first()
        
        if existing_analysis:
            logger.info(f"Analyse existante trouvée pour {domain}")
            return Response({
                'success': True,
                'message': 'Analyse récupérée depuis le cache',
                'data': WebsiteAnalysisSerializer(existing_analysis).data
            })
        
        # Nouvelle analyse
        logger.info(f"Début de l'analyse pour {domain}")
        
        # Extraire les documents juridiques
        extractor = DocumentExtractor()
        documents, extracted_domain = extractor.extract_all_documents(url)
        
        if not documents:
            # Créer une entrée d'échec
            analysis = WebsiteAnalysis.objects.create(
                domain=domain,
                url=url,
                summary="Aucun document juridique trouvé sur ce site.",
                is_successful=False,
                error_message="Aucun document juridique détecté"
            )
            
            return Response({
                'success': False,
                'message': 'Aucun document juridique trouvé sur ce site',
                'data': WebsiteAnalysisSerializer(analysis).data
            }, status=status.HTTP_404_NOT_FOUND)
        
        logger.info(f"Documents trouvés: {len(documents)}")
        
        # Analyser avec l'IA
        ai_analysis = analyze_legal_documents(documents, domain)
        
        # Créer l'analyse en base
        analysis = WebsiteAnalysis.objects.create(
            domain=domain,
            url=url,
            summary=ai_analysis.get('summary', ''),
            key_points=ai_analysis.get('key_points', []),
            what_you_accept=ai_analysis.get('what_you_accept', ''),
            data_collected=ai_analysis.get('data_collected', ''),
            data_usage=ai_analysis.get('data_usage', ''),
            data_sharing=ai_analysis.get('data_sharing', ''),
            retention_period=ai_analysis.get('retention_period', ''),
            critical_points=ai_analysis.get('critical_points', ''),
            readability_score=ai_analysis.get('readability_score', 5),
            risk_level=ai_analysis.get('risk_level', 'moderate'),
            documents_found=[{
                'type': doc['type'],
                'url': doc['url'],
                'title': doc['title']
            } for doc in documents],
            is_successful=True
        )
        
        # Sauvegarder les documents individuels
        for doc in documents:
            LegalDocument.objects.create(
                analysis=analysis,
                document_type=doc['type'],
                url=doc['url'],
                title=doc['title'],
                content=doc['content']
            )
        
        logger.info(f"Analyse terminée avec succès pour {domain}")
        
        return Response({
            'success': True,
            'message': 'Analyse terminée avec succès',
            'data': WebsiteAnalysisSerializer(analysis).data
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de {url}: {str(e)}")
        
        # Créer une entrée d'erreur
        try:
            analysis = WebsiteAnalysis.objects.create(
                domain=domain,
                url=url,
                summary=f"Erreur lors de l'analyse: {str(e)}",
                is_successful=False,
                error_message=str(e)
            )
            
            return Response({
                'success': False,
                'message': f'Erreur lors de l\'analyse: {str(e)}',
                'data': WebsiteAnalysisSerializer(analysis).data
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except:
            return Response({
                'success': False,
                'message': f'Erreur critique lors de l\'analyse: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_analysis(request, domain):
    """
    Récupère une analyse existante par domaine
    
    GET /api/analysis/{domain}/
    """
    
    try:
        analysis = get_object_or_404(
            WebsiteAnalysis, 
            domain=domain.lower(),
            is_successful=True
        )
        
        return Response({
            'success': True,
            'message': 'Analyse trouvée',
            'data': WebsiteAnalysisSerializer(analysis).data
        })
        
    except:
        return Response({
            'success': False,
            'message': 'Aucune analyse trouvée pour ce domaine'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def list_analyses(request):
    """
    Liste toutes les analyses réussies
    
    GET /api/analyses/
    """
    
    analyses = WebsiteAnalysis.objects.filter(
        is_successful=True
    ).order_by('-created_at')[:50]  # Limiter à 50 résultats
    
    return Response({
        'success': True,
        'message': f'{len(analyses)} analyses trouvées',
        'data': WebsiteAnalysisSerializer(analyses, many=True).data
    })


@api_view(['GET'])
def health_check(request):
    """
    Endpoint de vérification de santé de l'API
    
    GET /api/health/
    """
    
    return Response({
        'status': 'healthy',
        'message': 'API Legal Document Analyzer opérationnelle',
        'timestamp': timezone.now().isoformat()
    })

