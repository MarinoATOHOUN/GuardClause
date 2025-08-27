import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Loader2, Search, Shield, AlertTriangle, CheckCircle, Globe, FileText, Users, Clock, Share2, Database } from 'lucide-react'
import './App.css'

function App() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [analysis, setAnalysis] = useState(null)
  const [error, setError] = useState('')

  const analyzeWebsite = async () => {
    if (!url.trim()) {
      setError('Veuillez entrer une URL valide')
      return
    }

    setLoading(true)
    setError('')
    setAnalysis(null)

    try {
      const response = await fetch('http://localhost:8000/api/analyze/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url.trim() })
      })

      const data = await response.json()

      if (data.success) {
        setAnalysis(data.data)
      } else {
        setError(data.message || 'Erreur lors de l\'analyse')
      }
    } catch (err) {
      setError('Erreur de connexion au serveur')
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'low': return 'bg-green-100 text-green-800 border-green-200'
      case 'moderate': return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'high': return 'bg-red-100 text-red-800 border-red-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getRiskIcon = (riskLevel) => {
    switch (riskLevel) {
      case 'low': return <CheckCircle className="w-4 h-4" />
      case 'moderate': return <AlertTriangle className="w-4 h-4" />
      case 'high': return <Shield className="w-4 h-4" />
      default: return <AlertTriangle className="w-4 h-4" />
    }
  }

  const getReadabilityColor = (score) => {
    if (score >= 8) return 'text-green-600'
    if (score >= 6) return 'text-orange-600'
    return 'text-red-600'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <FileText className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Analyseur Juridique</h1>
                <p className="text-sm text-gray-600">Simplifiez vos documents légaux</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        {!analysis && (
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Comprenez facilement les documents juridiques des sites web
            </h2>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Analysez automatiquement les Conditions d'Utilisation, Politiques de Confidentialité et autres documents légaux. 
              Obtenez un résumé clair, des points clés et une évaluation des risques.
            </p>
          </div>
        )}

        {/* Search Section */}
        <Card className="mb-8 shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Globe className="w-5 h-5" />
              <span>Analyser un site web</span>
            </CardTitle>
            <CardDescription>
              Entrez l'URL d'un site web pour analyser ses documents juridiques
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex space-x-4">
              <Input
                type="url"
                placeholder="https://example.com"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="flex-1"
                onKeyPress={(e) => e.key === 'Enter' && analyzeWebsite()}
              />
              <Button 
                onClick={analyzeWebsite} 
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Analyse...
                  </>
                ) : (
                  <>
                    <Search className="w-4 h-4 mr-2" />
                    Analyser
                  </>
                )}
              </Button>
            </div>
            
            {error && (
              <Alert className="mt-4 border-red-200 bg-red-50">
                <AlertTriangle className="w-4 h-4" />
                <AlertDescription className="text-red-800">{error}</AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* Analysis Results */}
        {analysis && (
          <div className="space-y-6">
            {/* Summary Card */}
            <Card className="shadow-lg">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-2xl">Analyse de {analysis.domain}</CardTitle>
                  <div className="flex items-center space-x-4">
                    <Badge className={`${getRiskColor(analysis.risk_level)} flex items-center space-x-1`}>
                      {getRiskIcon(analysis.risk_level)}
                      <span>Risque {analysis.risk_level_display}</span>
                    </Badge>
                    <div className="text-right">
                      <div className="text-sm text-gray-600">Lisibilité</div>
                      <div className={`text-2xl font-bold ${getReadabilityColor(analysis.readability_score)}`}>
                        {analysis.readability_score}/10
                      </div>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="prose max-w-none">
                  <h3 className="text-lg font-semibold mb-3">Résumé</h3>
                  <p className="text-gray-700 leading-relaxed">{analysis.summary}</p>
                </div>
              </CardContent>
            </Card>

            {/* Detailed Analysis Grid */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* What You Accept */}
              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <CheckCircle className="w-5 h-5 text-blue-600" />
                    <span>Ce que vous acceptez</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700">{analysis.what_you_accept || 'Information non disponible'}</p>
                </CardContent>
              </Card>

              {/* Data Collected */}
              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Database className="w-5 h-5 text-purple-600" />
                    <span>Données collectées</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700">{analysis.data_collected || 'Information non disponible'}</p>
                </CardContent>
              </Card>

              {/* Data Usage */}
              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Users className="w-5 h-5 text-green-600" />
                    <span>Utilisation des données</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700">{analysis.data_usage || 'Information non disponible'}</p>
                </CardContent>
              </Card>

              {/* Data Sharing */}
              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Share2 className="w-5 h-5 text-orange-600" />
                    <span>Partage des données</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700">{analysis.data_sharing || 'Information non disponible'}</p>
                </CardContent>
              </Card>

              {/* Retention Period */}
              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Clock className="w-5 h-5 text-indigo-600" />
                    <span>Durée de conservation</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700">{analysis.retention_period || 'Information non disponible'}</p>
                </CardContent>
              </Card>

              {/* Critical Points */}
              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <AlertTriangle className="w-5 h-5 text-red-600" />
                    <span>Points critiques</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700">{analysis.critical_points || 'Aucun point critique identifié'}</p>
                </CardContent>
              </Card>
            </div>

            {/* Key Points */}
            {analysis.key_points && analysis.key_points.length > 0 && (
              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle>Points clés à retenir</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {analysis.key_points.map((point, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-600 mt-1 flex-shrink-0" />
                        <span className="text-gray-700">{point}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            {/* Documents Found */}
            {analysis.documents_found && analysis.documents_found.length > 0 && (
              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle>Documents analysés</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {analysis.documents_found.map((doc, index) => (
                      <div key={index} className="border rounded-lg p-3 bg-gray-50">
                        <div className="flex items-center space-x-2 mb-2">
                          <FileText className="w-4 h-4 text-blue-600" />
                          <span className="font-medium text-sm">{doc.title || doc.type}</span>
                        </div>
                        <a 
                          href={doc.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:underline break-all"
                        >
                          {doc.url}
                        </a>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* New Analysis Button */}
            <div className="text-center">
              <Button 
                onClick={() => {
                  setAnalysis(null)
                  setUrl('')
                  setError('')
                }}
                variant="outline"
                className="bg-white"
              >
                Analyser un autre site
              </Button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-600">
            <p>© 2025 Analyseur de Documents Juridiques - Simplifiez vos CGU et Politiques</p>
            <p className="text-sm mt-2">Outil d'analyse automatique pour une meilleure compréhension des documents légaux</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App

