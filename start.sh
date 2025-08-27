#!/bin/bash

# Script de démarrage rapide pour l'Analyseur de Documents Juridiques

echo "🚀 Démarrage de l'Analyseur de Documents Juridiques"
echo "=================================================="

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier si le fichier .env existe
if [ ! -f .env ]; then
    echo "📝 Création du fichier .env..."
    cp .env.example .env
    echo "⚠️  Veuillez éditer le fichier .env avec vos paramètres (notamment OPENAI_API_KEY)"
    echo "   Puis relancez ce script."
    exit 1
fi

# Vérifier si la clé OpenAI est configurée
if grep -q "your-openai-api-key-here" .env; then
    echo "⚠️  Veuillez configurer votre clé OPENAI_API_KEY dans le fichier .env"
    #exit 1
fi

echo "🔧 Construction des images Docker..."
docker-compose build

echo "🗄️  Démarrage des services..."
docker-compose up -d

echo "⏳ Attente du démarrage des services..."
sleep 30

# Vérifier que les services sont en cours d'exécution
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services démarrés avec succès !"
    echo ""
    echo "🌐 Accès à l'application :"
    echo "   Frontend : http://localhost"
    echo "   Backend API : http://localhost:8000"
    echo "   Admin Django : http://localhost:8000/admin"
    echo ""
    echo "📊 Vérification de l'état des services :"
    docker-compose ps
    echo ""
    echo "📝 Pour voir les logs :"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 Pour arrêter les services :"
    echo "   docker-compose down"
else
    echo "❌ Erreur lors du démarrage des services"
    echo "📝 Vérifiez les logs avec : docker-compose logs"
    exit 1
fi

