from django.db import models
from django.utils import timezone


class WebsiteAnalysis(models.Model):
    """Modèle pour stocker les analyses des sites web"""
    
    RISK_CHOICES = [
        ('low', 'Faible'),
        ('moderate', 'Modéré'),
        ('high', 'Élevé'),
    ]
    
    # Informations de base
    domain = models.CharField(max_length=255, unique=True, verbose_name="Domaine")
    url = models.URLField(verbose_name="URL d'origine")
    
    # Résultats de l'analyse
    summary = models.TextField(verbose_name="Résumé")
    key_points = models.JSONField(default=dict, verbose_name="Points clés")
    
    # Sections d'analyse
    what_you_accept = models.TextField(blank=True, verbose_name="Ce que vous acceptez")
    data_collected = models.TextField(blank=True, verbose_name="Données collectées")
    data_usage = models.TextField(blank=True, verbose_name="Utilisation des données")
    data_sharing = models.TextField(blank=True, verbose_name="Partage des données")
    retention_period = models.TextField(blank=True, verbose_name="Durée de conservation")
    critical_points = models.TextField(blank=True, verbose_name="Points critiques")
    
    # Scores
    readability_score = models.IntegerField(default=0, verbose_name="Score de lisibilité (1-10)")
    risk_level = models.CharField(
        max_length=10, 
        choices=RISK_CHOICES, 
        default='moderate',
        verbose_name="Niveau de risque"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    # Documents trouvés
    documents_found = models.JSONField(default=list, verbose_name="Documents trouvés")
    
    # Statut de l'analyse
    is_successful = models.BooleanField(default=True, verbose_name="Analyse réussie")
    error_message = models.TextField(blank=True, verbose_name="Message d'erreur")
    
    class Meta:
        verbose_name = "Analyse de site web"
        verbose_name_plural = "Analyses de sites web"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Analyse de {self.domain}"


class LegalDocument(models.Model):
    """Modèle pour stocker les documents juridiques individuels"""
    
    DOCUMENT_TYPES = [
        ('terms', 'Conditions d\'utilisation'),
        ('privacy', 'Politique de confidentialité'),
        ('cookies', 'Politique de cookies'),
        ('legal', 'Mentions légales'),
        ('other', 'Autre'),
    ]
    
    analysis = models.ForeignKey(
        WebsiteAnalysis, 
        on_delete=models.CASCADE, 
        related_name='documents',
        verbose_name="Analyse"
    )
    
    document_type = models.CharField(
        max_length=20, 
        choices=DOCUMENT_TYPES,
        verbose_name="Type de document"
    )
    
    url = models.URLField(verbose_name="URL du document")
    title = models.CharField(max_length=500, blank=True, verbose_name="Titre")
    content = models.TextField(verbose_name="Contenu")
    
    # Métadonnées
    extracted_at = models.DateTimeField(default=timezone.now, verbose_name="Date d'extraction")
    content_length = models.IntegerField(default=0, verbose_name="Longueur du contenu")
    
    class Meta:
        verbose_name = "Document juridique"
        verbose_name_plural = "Documents juridiques"
        unique_together = ['analysis', 'url']
    
    def save(self, *args, **kwargs):
        if self.content:
            self.content_length = len(self.content)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.analysis.domain}"

