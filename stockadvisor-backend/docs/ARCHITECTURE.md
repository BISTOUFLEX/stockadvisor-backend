# Architecture du Backend StockAdvisor+ Bot

## 📐 Vue d'Ensemble

Le backend est une application Python FastAPI qui orchestre un agent IA conversationnel. Il utilise le Model Context Protocol (MCP) pour exposer des outils d'analyse financière.

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                          │
└─────────────────────────────────────────────────────────────┘
                            │
                   (HTTP/WebSocket)
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend (Python - FastAPI)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ API Routes (FastAPI)                                │  │
│  │ • /api/chat - Conversation                          │  │
│  │ • /api/analyze - Analyse d'action                   │  │
│  │ • /api/compare - Comparaison d'actions              │  │
│  │ • /api/news - Actualités                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│                            ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Agent Orchestrator                                   │  │
│  │ • Gestion du contexte conversationnel                │  │
│  │ • Décision des outils à utiliser                     │  │
│  │ • Génération de réponses naturelles                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│         ┌──────────────────┼──────────────────┐             │
│         ▼                  ▼                  ▼             │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐        │
│  │   Ollama   │    │    MCP     │    │  Database  │        │
│  │   (LLM)    │    │   Server   │    │  (Cache)   │        │
│  └────────────┘    └────────────┘    └────────────┘        │
│                            │                                 │
│         ┌──────────────────┼──────────────────┐             │
│         ▼                  ▼                  ▼             │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐        │
│  │  Scraper   │    │  Analyzer  │    │ Generator  │        │
│  │   Stock    │    │ Technique  │    │  Rapports  │        │
│  │   News     │    │ Sentiment  │    │  Alertes   │        │
│  └────────────┘    └────────────┘    └────────────┘        │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
    ┌─────────┐          ┌─────────┐         ┌──────────┐
    │ Yahoo   │          │ Reuters │         │ Bloomberg│
    │ Finance │          │ Bloomberg         │ CNBC     │
    │         │          │ CNBC    │         │ MarketW  │
    └─────────┘          └─────────┘         └──────────┘
```

## 🏗️ Composants Principaux

### 1. **FastAPI Application** (`src/main.py`)
- Point d'entrée de l'application
- Configuration CORS pour le frontend
- Initialisation des composants
- Gestion du cycle de vie

### 2. **Agent Orchestrator** (`src/agent/orchestrator.py`)
- Gère la logique de l'agent IA
- Maintient les contextes utilisateur
- Décide quels outils utiliser
- Génère les réponses

**Flux de traitement** :
```
Message utilisateur
    ↓
Ajouter au contexte
    ↓
Générer prompt système
    ↓
Envoyer à Ollama
    ↓
Ollama décide des outils
    ↓
Exécuter les outils via MCP
    ↓
Synthétiser la réponse
    ↓
Retourner au frontend
```

### 3. **Conversation Context** (`src/agent/context.py`)
- Gère l'historique de conversation
- Stocke les préférences utilisateur
- Maintient la liste des actions suivies
- Génère les prompts système

### 4. **MCP Server** (`src/mcp/server.py`)
- Orchestre tous les outils disponibles
- Expose une interface unifiée
- Gère l'exécution des outils

### 5. **Ollama Client** (`src/ollama/client.py`)
- Communication avec le service Ollama local
- Génération de texte
- Streaming de réponses
- Health check

### 6. **Outils MCP** (`src/mcp/tools/`)

#### Stock Scraper (`scraper_stock.py`)
```python
# Récupère les données de Yahoo Finance
stock_data = await scraper.get_stock_data("AAPL")
# Récupère les données historiques
historical = await scraper.get_historical_data("AAPL", "1y")
```

#### News Scraper (`scraper_news.py`)
```python
# Récupère les actualités pour un symbole
news = await scraper.get_news_for_symbol("AAPL", limit=10)
# Récupère les actualités du marché
market_news = await scraper.get_market_news(limit=20)
```

#### Technical Analyzer (`analyzer.py`)
```python
# Calcule les indicateurs
ma = TechnicalAnalyzer.calculate_moving_average(prices, 20)
rsi = TechnicalAnalyzer.calculate_rsi(prices)
macd = TechnicalAnalyzer.calculate_macd(prices)
trend = TechnicalAnalyzer.analyze_trend(prices)
```

#### Sentiment Analyzer (`analyzer.py`)
```python
# Analyse le sentiment du texte
sentiment = SentimentAnalyzer.analyze_text(text)
# Analyse le sentiment des actualités
news_sentiment = SentimentAnalyzer.analyze_news_sentiment(articles)
```

#### Report Generator (`generator.py`)
```python
# Génère un rapport d'analyse complet
report = ReportGenerator.generate_stock_analysis_report(...)
# Génère un rapport de comparaison
comparison = ReportGenerator.generate_comparison_report(...)
```

### 7. **API Routes** (`src/api/routes.py`)

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health` | GET | Vérifier l'état du service |
| `/chat` | POST | Envoyer un message au chatbot |
| `/analyze` | POST | Analyser une action |
| `/compare` | POST | Comparer des actions |
| `/news` | GET | Obtenir les actualités |
| `/tools` | GET | Lister les outils disponibles |
| `/context/{user_id}` | DELETE | Effacer le contexte utilisateur |

## 🔄 Flux de Données

### Flux de Chat (Exemple)

```
1. Frontend envoie : POST /api/chat
   {
     "user_id": "user123",
     "message": "Analyse Apple"
   }

2. Backend reçoit et traite :
   - Récupère/crée le contexte utilisateur
   - Ajoute le message à l'historique
   - Génère le prompt système
   - Envoie à Ollama

3. Ollama décide des outils :
   - Analyse le message
   - Décide d'utiliser analyze_stock("AAPL")
   - Retourne la décision au backend

4. Backend exécute les outils :
   - Appelle MCP.analyze_stock("AAPL")
   - MCP scrape les données
   - MCP analyse les indicateurs
   - MCP scrape les actualités
   - MCP analyse le sentiment
   - MCP génère le rapport

5. Backend synthétise :
   - Envoie les résultats à Ollama
   - Ollama génère une réponse naturelle
   - Backend ajoute la réponse au contexte

6. Frontend reçoit :
   {
     "success": true,
     "response": "Apple montre une tendance...",
     "analysis": { ... },
     "tools_used": ["analyze_stock"]
   }
```

## 📦 Structure des Paquets

```
src/
├── main.py                    # Application FastAPI
├── __init__.py
│
├── agent/                     # Logique de l'agent
│   ├── __init__.py
│   ├── orchestrator.py        # Orchestration
│   └── context.py             # Gestion du contexte
│
├── mcp/                       # Model Context Protocol
│   ├── __init__.py
│   ├── server.py              # Serveur MCP
│   └── tools/                 # Outils
│       ├── __init__.py
│       ├── scraper_stock.py
│       ├── scraper_news.py
│       ├── analyzer.py
│       └── generator.py
│
├── ollama/                    # Intégration Ollama
│   ├── __init__.py
│   └── client.py
│
├── api/                       # API FastAPI
│   ├── __init__.py
│   ├── routes.py              # Endpoints
│   └── schemas.py             # Modèles Pydantic
│
├── database/                  # Base de données
│   └── __init__.py
│
└── utils/                     # Utilitaires
    ├── __init__.py
    ├── config.py              # Configuration
    └── logger.py              # Logging
```

## 🔐 Sécurité

### CORS
- Limité au frontend uniquement
- Configurable via `FRONTEND_URL`

### Validation
- Pydantic pour la validation des entrées
- Typage statique avec type hints

### Gestion des Erreurs
- Erreurs sans exposition de détails sensibles
- Logging complet des erreurs

### Scraping Responsable
- Délais configurables entre requêtes
- Respect des conditions d'utilisation
- User-agent approprié

## 📊 Modèles de Données

### Message
```python
{
  "role": "user" | "assistant",
  "content": str,
  "timestamp": ISO8601,
  "metadata": Dict
}
```

### Stock Data
```python
{
  "symbol": str,
  "price": float,
  "currency": str,
  "market_cap": float,
  "pe_ratio": float,
  "dividend_yield": float,
  "timestamp": ISO8601
}
```

### Analysis Report
```python
{
  "symbol": str,
  "timestamp": ISO8601,
  "current_price": float,
  "technical_analysis": {...},
  "news_sentiment": {...},
  "recommendation": "BUY" | "SELL" | "HOLD",
  "confidence": float,
  "rationale": str,
  "summary": str,
  "metrics": {...}
}
```

## 🧪 Tests

- **Unit Tests**: Tests des composants individuels
- **Integration Tests**: Tests des interactions entre composants
- **Coverage**: Cible > 80%

```bash
pytest tests/ -v --cov=src
```

## 📈 Performance

### Optimisations
- Cache des données boursières
- Réutilisation des connexions HTTP
- Async/await pour les opérations I/O
- Streaming des réponses

### Limitations Connues
- Ollama doit être en local (pas de service cloud)
- Scraping limité par les délais de politesse
- Pas de persistance des données entre redémarrages

## 🚀 Déploiement

### Prérequis
- Python 3.11+
- Ollama en cours d'exécution
- Variables d'environnement configurées

### Lancement
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Production
- Utiliser Gunicorn/Uvicorn
- Configurer un reverse proxy (Nginx)
- Mettre en place un monitoring
- Configurer les logs centralisés
