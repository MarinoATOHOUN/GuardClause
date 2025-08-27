import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


class DocumentExtractor:
    """Classe pour extraire les documents juridiques des sites web"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Patterns pour identifier les documents juridiques
        self.legal_patterns = {
            'terms': [
                r'terms?[-_\s]*(of[-_\s]*)?use',
                r'terms?[-_\s]*(of[-_\s]*)?service',
                r'terms?[-_\s]*and[-_\s]*conditions?',
                r'conditions?[-_\s]*(of[-_\s]*)?use',
                r'user[-_\s]*agreement',
                r'cgu',
                r'cgv'
            ],
            'privacy': [
                r'privacy[-_\s]*policy',
                r'privacy[-_\s]*notice',
                r'data[-_\s]*protection',
                r'confidentialit[eé]',
                r'donn[eé]es[-_\s]*personnelles'
            ],
            'cookies': [
                r'cookie[-_\s]*policy',
                r'cookie[-_\s]*notice',
                r'cookies?'
            ],
            'legal': [
                r'legal[-_\s]*notice',
                r'mentions?[-_\s]*l[eé]gales?',
                r'legal[-_\s]*information',
                r'imprint'
            ]
        }
    
    def normalize_url(self, url: str) -> str:
        """Normalise l'URL d'entrée"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    def get_domain(self, url: str) -> str:
        """Extrait le domaine de l'URL"""
        parsed = urlparse(url)
        return parsed.netloc.lower()
    
    def find_legal_document_urls(self, base_url: str) -> List[Dict[str, str]]:
        """
        Trouve les URLs des documents juridiques sur un site
        
        Returns:
            List[Dict]: Liste des documents trouvés avec type et URL
        """
        try:
            response = self.session.get(base_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            found_documents = []
            
            # Chercher dans tous les liens
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '').lower()
                text = link.get_text(strip=True).lower()
                
                # Construire l'URL complète
                full_url = urljoin(base_url, link['href'])
                
                # Identifier le type de document
                doc_type = self._identify_document_type(href, text)
                
                if doc_type:
                    found_documents.append({
                        'type': doc_type,
                        'url': full_url,
                        'text': link.get_text(strip=True)
                    })
            
            # Supprimer les doublons
            unique_docs = []
            seen_urls = set()
            
            for doc in found_documents:
                if doc['url'] not in seen_urls:
                    unique_docs.append(doc)
                    seen_urls.add(doc['url'])
            
            # Essayer des URLs communes si rien n'est trouvé
            if not unique_docs:
                unique_docs = self._try_common_urls(base_url)
            
            return unique_docs
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche des documents: {str(e)}")
            return self._try_common_urls(base_url)
    
    def _identify_document_type(self, href: str, text: str) -> str:
        """Identifie le type de document basé sur l'URL et le texte"""
        combined = f"{href} {text}".lower()
        
        for doc_type, patterns in self.legal_patterns.items():
            for pattern in patterns:
                if re.search(pattern, combined, re.IGNORECASE):
                    return doc_type
        
        return None
    
    def _try_common_urls(self, base_url: str) -> List[Dict[str, str]]:
        """Essaie des URLs communes pour les documents juridiques"""
        common_paths = [
            ('/terms', 'terms'),
            ('/terms-of-use', 'terms'),
            ('/terms-of-service', 'terms'),
            ('/privacy', 'privacy'),
            ('/privacy-policy', 'privacy'),
            ('/legal', 'legal'),
            ('/cookies', 'cookies'),
            ('/cgu', 'terms'),
            ('/cgv', 'terms'),
            ('/mentions-legales', 'legal'),
            ('/confidentialite', 'privacy')
        ]
        
        found_documents = []
        
        for path, doc_type in common_paths:
            try:
                test_url = urljoin(base_url, path)
                response = self.session.head(test_url, timeout=5)
                
                if response.status_code == 200:
                    found_documents.append({
                        'type': doc_type,
                        'url': test_url,
                        'text': path.strip('/')
                    })
            except:
                continue
        
        return found_documents
    
    def extract_document_content(self, url: str) -> Dict[str, str]:
        """
        Extrait le contenu d'un document juridique
        
        Returns:
            Dict: Contenu du document avec titre et texte
        """
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Supprimer les éléments non pertinents
            for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()
            
            # Extraire le titre
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
            
            # Chercher le titre dans les balises h1, h2
            if not title:
                for tag in soup.find_all(['h1', 'h2']):
                    title = tag.get_text(strip=True)
                    break
            
            # Extraire le contenu principal
            content = ""
            
            # Essayer de trouver le contenu principal
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|body'))
            
            if main_content:
                content = main_content.get_text(separator='\n', strip=True)
            else:
                # Fallback: prendre tout le body
                body = soup.find('body')
                if body:
                    content = body.get_text(separator='\n', strip=True)
            
            # Nettoyer le contenu
            content = self._clean_content(content)
            
            return {
                'title': title,
                'content': content,
                'url': url
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du contenu de {url}: {str(e)}")
            return {
                'title': f"Erreur d'extraction",
                'content': f"Impossible d'extraire le contenu: {str(e)}",
                'url': url
            }
    
    def _clean_content(self, content: str) -> str:
        """Nettoie le contenu extrait"""
        # Supprimer les lignes vides multiples
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # Supprimer les espaces en début et fin
        content = content.strip()
        
        # Limiter la taille si trop long
        if len(content) > 100000:
            content = content[:100000] + "... [contenu tronqué]"
        
        return content
    
    def extract_all_documents(self, url: str) -> Tuple[List[Dict], str]:
        """
        Extrait tous les documents juridiques d'un site
        
        Returns:
            Tuple: (liste des documents, domaine)
        """
        normalized_url = self.normalize_url(url)
        domain = self.get_domain(normalized_url)
        
        # Trouver les URLs des documents
        document_urls = self.find_legal_document_urls(normalized_url)
        
        # Extraire le contenu de chaque document
        documents = []
        for doc_info in document_urls:
            content = self.extract_document_content(doc_info['url'])
            content.update({
                'type': doc_info['type'],
                'link_text': doc_info['text']
            })
            documents.append(content)
        
        return documents, domain

