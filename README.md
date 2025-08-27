# 📋 Analyseur de Documents Juridiques

Une application web fullstack moderne qui permet d'analyser et de simplifier automatiquement les documents juridiques des sites web (Conditions d'Utilisation, Politiques de Confidentialité, etc.).

## 🚀 Fonctionnalités

### 🔙 Backend (Django REST API)
- **Extraction automatique** des URLs des documents juridiques
- **Téléchargement et parsing** du contenu des pages
- **Analyse IA** avec résumé, points clés et évaluation des risques
- **Base de données PostgreSQL** pour stocker les analyses
- **API REST** complète avec gestion d'erreurs

### 🎨 Frontend (React)
- **Interface moderne** avec Tailwind CSS et shadcn/ui
- **Barre de recherche** intuitive
- **Affichage structuré** des résultats d'analyse
- **Éléments visuels** (icônes, scores, pastilles de risque)
- **Design responsive** pour mobile et desktop

### 🧠 Intelligence Artificielle
- **Résumé automatique** en langage clair
- **Identification des risques** et points critiques
- **Score de lisibilité** (1-10)
- **Évaluation du niveau de risque** (faible, modéré, élevé)

## 📁 Structure du Projet

```
legal_doc_analyzer/
├── backend/                    # API Django REST
│   ├── legal_analyzer/        # Configuration Django
│   ├── analyzer/              # Application principale
│   │   ├── models.py          # Modèles de données
│   │   ├── views.py           # Vues API
│   │   ├── serializers.py     # Serializers REST
│   │   ├── document_extractor.py  # Extraction de documents
│   │   └── llm_utils.py       # Intégration IA
│   ├── requirements.txt       # Dépendances Python
│   └── .env.example          # Variables d'environnement
├── frontend/                  # Application React
│   └── legal-doc-analyzer-frontend/
│       ├── src/
│       │   ├── App.jsx        # Composant principal
│       │   └── components/    # Composants UI
│       └── package.json       # Dépendances Node.js
└── README.md                  # Documentation
```

## 🛠️ Installation

### Prérequis
- Python 3.11+
- Node.js 20+
- PostgreSQL 14+
- Clé API OpenAI (ou compatible)

### 1. Cloner le projet
```bash
git clone <repository-url>
cd legal_doc_analyzer
```

### 2. Configuration du Backend

#### Installation des dépendances
```bash
cd backend
pip install -r requirements.txt
```

#### Configuration de la base de données
```bash
# Installer PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Démarrer le service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Créer la base de données
sudo -u postgres createdb legal_analyzer
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
```

#### Variables d'environnement
```bash
cp .env.example .env
# Éditer le fichier .env avec vos paramètres
```

Contenu du fichier `.env` :
```env
# Configuration Django
SECRET_KEY=your-secret-key-here
DEBUG=True

# Base de données PostgreSQL
DB_NAME=legal_analyzer
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# API OpenAI
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1
```

#### Migrations et démarrage
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### 3. Configuration du Frontend

```bash
cd frontend/legal-doc-analyzer-frontend
pnpm install
pnpm run dev --host
```

L'application sera accessible sur :
- **Frontend** : http://localhost:5174
- **Backend API** : http://localhost:8000

## 📖 Utilisation

### Interface Web
1. Ouvrez http://localhost:5174 dans votre navigateur
2. Entrez l'URL d'un site web dans la barre de recherche
3. Cliquez sur "Analyser"
4. Consultez les résultats structurés

### API REST

#### Analyser un site web
```bash
curl -X POST http://localhost:8000/api/analyze/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

#### Récupérer une analyse existante
```bash
curl http://localhost:8000/api/analysis/example.com/
```

#### Lister toutes les analyses
```bash
curl http://localhost:8000/api/analyses/
```

#### Vérification de santé
```bash
curl http://localhost:8000/api/health/
```

## 🔧 Configuration Avancée

### Modèles IA Supportés
L'application supporte plusieurs modèles via l'API OpenAI :
- `gpt-3.5-turbo` (recommandé)
- `gpt-4`
- Modèles compatibles OpenAI

### Personnalisation de l'Extraction
Modifiez `backend/analyzer/document_extractor.py` pour :
- Ajouter de nouveaux patterns de détection
- Personnaliser les URLs communes
- Améliorer le parsing du contenu

### Personnalisation de l'Analyse IA
Modifiez `backend/analyzer/llm_utils.py` pour :
- Ajuster les prompts d'analyse
- Modifier les critères d'évaluation
- Personnaliser les scores de risque

## 🐳 Déploiement avec Docker

### Backend
```dockerfile
# Dockerfile pour le backend
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "legal_analyzer.wsgi:application"]
```

### Frontend
```dockerfile
# Dockerfile pour le frontend
FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
EXPOSE 80
```

### Docker Compose
```yaml
version: '3.8'
services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: legal_analyzer
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DB_HOST=db

  frontend:
    build: ./frontend/legal-doc-analyzer-frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

## 🧪 Tests

### Backend
```bash
cd backend
python manage.py test
```

### Frontend
```bash
cd frontend/legal-doc-analyzer-frontend
pnpm test
```

## 📊 Monitoring et Logs

### Logs Django
```bash
# Activer les logs détaillés dans settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'legal_analyzer.log',
        },
    },
    'loggers': {
        'analyzer': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 🔒 Sécurité

### Recommandations de Production
- Utilisez HTTPS en production
- Configurez des clés secrètes robustes
- Limitez les origines CORS
- Implémentez une authentification si nécessaire
- Surveillez les logs d'erreurs

### Variables d'Environnement Sensibles
- `SECRET_KEY` : Clé secrète Django
- `OPENAI_API_KEY` : Clé API pour l'IA
- `DB_PASSWORD` : Mot de passe de la base de données

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

Pour obtenir de l'aide :
1. Consultez la documentation
2. Vérifiez les issues existantes
3. Créez une nouvelle issue avec les détails du problème

## 🔄 Changelog

### Version 1.0.0
- ✅ Extraction automatique des documents juridiques
- ✅ Analyse IA avec OpenAI
- ✅ Interface React moderne
- ✅ API REST complète
- ✅ Base de données PostgreSQL
- ✅ Design responsive

---

**Développé avec ❤️ pour simplifier la compréhension des documents juridiques**

