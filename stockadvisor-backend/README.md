# StockAdvisor+ Bot - Backend

Backend Python pour l'agent IA conversationnel d'analyse boursière.

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.11+
- Ollama installé et en cours d'exécution
- pip ou poetry

### Installation

1. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditer .env avec vos paramètres
```

4. **Démarrer Ollama** (dans un autre terminal)

- **Installer**: Assurez-vous qu'Ollama est installé (Ollama Desktop ou le client CLI). Sur Windows, vous pouvez utiliser l'installateur officiel ou `winget` si disponible.
- **Démarrer (PowerShell)**:
```powershell
ollama serve
```
- **Vérifier**: dans un autre terminal, lister les modèles disponibles:
```powershell
ollama models
```
- **Remarques**: Ollama écoute par défaut sur `http://localhost:11434`. Vérifiez que la variable d'environnement `OLLAMA_HOST` dans votre `.env` correspond (par défaut `http://localhost:11434`). Exécutez `ollama serve` dans un terminal séparé avant de lancer le backend.

5. **Lancer le serveur backend**
```bash
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Le serveur sera disponible à `http://localhost:8000`

## 📁 Structure du Projet

```
src/
├── main.py                 # Point d'entrée FastAPI
├── agent/                  # Logique de l'agent IA
│   ├── orchestrator.py     # Orchestrateur d'agent
│   └── context.py          # Gestion du contexte conversationnel
├── mcp/                    # Model Context Protocol
│   ├── server.py           # Serveur MCP
│   └── tools/              # Outils disponibles
│       ├── scraper_stock.py
│       ├── scraper_news.py
│       ├── analyzer.py
│       └── generator.py
├── ollama/                 # Intégration Ollama
│   └── client.py           # Client Ollama
├── api/                    # Routes FastAPI
│   ├── routes.py           # Endpoints
│   └── schemas.py          # Modèles Pydantic
├── database/               # Modèles de base de données
├── utils/                  # Utilitaires
│   ├── config.py           # Configuration
│   └── logger.py           # Logging
└── __init__.py

tests/                      # Tests unitaires
```

## 🔌 Endpoints API

### Chat
- **POST** `/api/chat` - Envoyer un message au chatbot
```json
{
  "user_id": "user123",
  "message": "Analyse l'action Apple"
}
```

### Analyse
- **POST** `/api/analyze` - Analyser une action
```json
{
  "symbol": "AAPL"
}
```

### Comparaison
- **POST** `/api/compare` - Comparer plusieurs actions
```json
{
  "symbols": ["AAPL", "MSFT", "GOOGL"]
}
```

### Actualités
- **GET** `/api/news?limit=20` - Obtenir les actualités du marché

### Outils
- **GET** `/api/tools` - Lister les outils disponibles

### Santé
- **GET** `/api/health` - Vérifier l'état du service

## 🛠️ Outils MCP Disponibles

### 1. Scraper Stock
Récupère les données boursières en temps réel et historiques.
- Données actuelles (prix, market cap, P/E ratio, etc.)
- Données historiques (OHLCV)

### 2. Scraper News
Récupère les actualités financières de plusieurs sources.
- Reuters, Bloomberg, CNBC, MarketWatch
- Filtrage par symbole

### 3. Analyseur Technique
Calcule les indicateurs techniques.
- Moyennes mobiles (MA)
- Indice de force relative (RSI)
- MACD
- Analyse de tendance

### 4. Analyseur de Sentiment
Analyse le sentiment des actualités.
- Classification (positif/négatif/neutre)
- Score de sentiment

### 5. Générateur de Rapports
Génère des rapports d'analyse complets.
- Recommandations (Achat/Vente/Conserver)
- Synthèse des analyses
- Rapports de comparaison

## 🧪 Tests

Exécuter les tests unitaires :
```bash
pytest tests/ -v
```

Avec couverture :
```bash
pytest tests/ --cov=src --cov-report=html
```

## 📚 Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔧 Configuration

Les variables d'environnement principales :

| Variable | Description | Défaut |
|----------|-------------|--------|
| BACKEND_HOST | Adresse du serveur | 0.0.0.0 |
| BACKEND_PORT | Port du serveur | 8000 |
| OLLAMA_HOST | URL du service Ollama | http://localhost:11434 |
| OLLAMA_MODEL | Modèle Ollama à utiliser | mistral |
| FRONTEND_URL | URL du frontend (CORS) | http://localhost:3000 |
| DATABASE_URL | URL de la base de données | sqlite:///./stockadvisor.db |
| SCRAPING_DELAY | Délai entre les requêtes (s) | 2 |
| DEBUG | Mode debug | False |

## 🚨 Gestion des Erreurs

Le backend gère les erreurs suivantes :

- **503 Service Unavailable**: Ollama ou MCP non disponible
- **400 Bad Request**: Paramètres invalides
- **500 Internal Server Error**: Erreur serveur

Toutes les erreurs sont loggées dans les logs de l'application.

## 📝 Logging

Les logs sont écrits dans la console avec le format :
```
2024-01-09 12:34:56 - stockadvisor - INFO - Message
```

Niveaux de log : DEBUG, INFO, WARNING, ERROR, CRITICAL

## 🔐 Sécurité

- CORS activé pour le frontend uniquement
- Validation des entrées avec Pydantic
- Gestion des erreurs sans exposition de détails sensibles
- Délais de scraping respectueux

## 📦 Dépendances Principales

- **FastAPI**: Framework web
- **Uvicorn**: Serveur ASGI
- **Pydantic**: Validation des données
- **Ollama**: Client LLM
- **BeautifulSoup4**: Scraping HTML
- **Pandas**: Analyse de données
- **Requests**: Requêtes HTTP

## 🤝 Contribution

Pour contribuer au projet :

1. Créer une branche feature
2. Faire les modifications
3. Ajouter des tests
4. Créer une pull request

## 📄 Licence

MIT License

## 📞 Support

Pour toute question ou problème, veuillez ouvrir une issue sur le repository.
