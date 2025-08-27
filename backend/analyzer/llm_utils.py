import os
from openai import OpenAI
from django.conf import settings
import json
import logging
from decouple import config


import json
import re

def extract_json(text: str):
    """
    Extrait la partie JSON d'un texte qui contient du contenu supplémentaire (ex: commentaires IA).
    Retourne un dictionnaire Python.
    """
    try:
        # Trouver la première accolade ouvrante et la dernière fermante
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("Aucun JSON trouvé dans le texte.")
        
        json_str = match.group(0).strip()
        
        # Charger en objet Python
        #data = json.loads(json_str)
        return json_str
    except Exception as e:
        raise ValueError(f"Erreur lors de l'extraction du JSON : {e}")



logger = logging.getLogger(__name__)

# Configuration du client OpenAI
# openai.api_key = settings.OPENAI_API_KEY
# if hasattr(settings, 'OPENAI_API_BASE'):
#     openai.api_base = settings.OPENAI_API_BASE


def analyze_legal_documents(documents_content, domain):
    """
    Analyse les documents juridiques avec l'IA
    
    Args:
        documents_content (list): Liste des contenus des documents
        domain (str): Nom de domaine du site
    
    Returns:
        dict: Résultats de l'analyse
    """
    
    # Combiner tous les documents
    combined_content = "\n\n".join([
        f"=== {doc.get('title', 'Document')} ===\n{doc.get('content', '')}"
        for doc in documents_content
    ])
    
    # Limiter la taille du contenu pour éviter les erreurs de token
    if len(combined_content) > 50000:
        combined_content = combined_content[:50000] + "... [contenu tronqué]"
    
    prompt = f"""
Analysez les documents juridiques suivants du site web "{domain}" et fournissez une analyse structurée en français.

DOCUMENTS À ANALYSER:
{combined_content}

Veuillez fournir votre réponse au format JSON avec la structure suivante:

{{
    "summary": "Résumé général en langage clair et accessible (200-300 mots)",
    "what_you_accept": "Explication claire de ce que l'utilisateur accepte en utilisant le service",
    "data_collected": "Types de données collectées par le service",
    "data_usage": "Comment les données sont utilisées",
    "data_sharing": "Avec qui les données sont partagées",
    "retention_period": "Durée de conservation des données",
    "critical_points": "Points critiques et préoccupants pour l'utilisateur",
    "key_points": [
        "Point important 1",
        "Point important 2",
        "Point important 3"
    ],
    "readability_score": 7,
    "risk_level": "moderate",
    "risk_explanation": "Explication du niveau de risque attribué"
}}

INSTRUCTIONS:
- Utilisez un langage simple et accessible
- Le score de lisibilité va de 1 (très difficile) à 10 (très facile)
- Le niveau de risque peut être: "low", "moderate", ou "high"
- Identifiez les clauses problématiques ou inhabituelles
- Mettez l'accent sur les droits et obligations de l'utilisateur
- Soyez objectif et factuel dans votre analyse
- Fournissez directement la réponse en JSON sans explication supplémentaire
- La réponse doit commencer et se terminer par des balises de code JSON en suivant le format fournit ci-dessus
"""

    try:
        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=config('HF_TOKEN'),
        )
        
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3.1:fireworks-ai",
            messages=[
                {
                    "role": "system",
                    "content": "Vous êtes un expert juridique spécialisé dans l'analyse de documents juridiques web. Votre rôle est d'expliquer ces documents de manière claire et accessible au grand public."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )
        
        # Extraire le contenu de la réponse
        content = extract_json(response.choices[0].message.content.strip())
        
        print(content)
        # # Nettoyer le JSON si nécessaire
        # if content.startswith('```json'):
        #     content = content[7:]
        # if content.endswith('```'):
        #     content = content[:-3]
        
        # Parser le JSON
        try:
            analysis_result = json.loads(content)
        except json.JSONDecodeError:
            logger.error(f"Erreur de parsing JSON: {content}")
            # Fallback avec une structure de base
            analysis_result = {
                "summary": "Analyse automatique non disponible. Veuillez consulter les documents directement.",
                "what_you_accept": "Information non disponible",
                "data_collected": "Information non disponible",
                "data_usage": "Information non disponible", 
                "data_sharing": "Information non disponible",
                "retention_period": "Information non disponible",
                "critical_points": "Information non disponible",
                "key_points": ["Analyse automatique non disponible"],
                "readability_score": 5,
                "risk_level": "moderate",
                "risk_explanation": "Analyse automatique non disponible"
            }
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse LLM: {str(e)}")
        return {
            "summary": f"Erreur lors de l'analyse automatique: {str(e)}",
            "what_you_accept": "Information non disponible",
            "data_collected": "Information non disponible",
            "data_usage": "Information non disponible",
            "data_sharing": "Information non disponible", 
            "retention_period": "Information non disponible",
            "critical_points": "Information non disponible",
            "key_points": ["Erreur lors de l'analyse"],
            "readability_score": 1,
            "risk_level": "high",
            "risk_explanation": "Impossible d'analyser les documents"
        }


def get_risk_score_color(risk_level):
    """Retourne la couleur associée au niveau de risque"""
    colors = {
        'low': '#10B981',      # Vert
        'moderate': '#F59E0B', # Orange
        'high': '#EF4444'      # Rouge
    }
    return colors.get(risk_level, '#6B7280')  # Gris par défaut

