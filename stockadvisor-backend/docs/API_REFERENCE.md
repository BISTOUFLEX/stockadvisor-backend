# Documentation API - StockAdvisor+ Bot

## 🌐 Base URL

```
http://localhost:8000/api
```

## 📋 Endpoints

### 1. Health Check

**Endpoint**: `GET /health`

Vérifier l'état du service.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "ollama_available": true,
  "mcp_available": true,
  "timestamp": "2024-01-09T12:34:56.789Z"
}
```

---

### 2. Chat - Conversation

**Endpoint**: `POST /chat`

Envoyer un message au chatbot et recevoir une réponse intelligente.

**Request**:
```json
{
  "user_id": "user123",
  "message": "Analyse l'action Apple pour moi"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "user_id": "user123",
  "response": "Apple (AAPL) montre une tendance bullish...",
  "analysis": { ... },
  "tools_used": ["analyze_stock(AAPL)"]
}
```

---

### 3. Analyse - Stock Analysis

**Endpoint**: `POST /analyze`

Analyser complètement une action boursière.

**Request**:
```json
{
  "symbol": "AAPL"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "symbol": "AAPL",
  "report": {
    "symbol": "AAPL",
    "current_price": 185.50,
    "recommendation": "BUY",
    "confidence": 0.75,
    "technical_analysis": { ... },
    "news_sentiment": { ... }
  },
  "news": [ ... ]
}
```

---

### 4. Comparaison - Stock Comparison

**Endpoint**: `POST /compare`

Comparer plusieurs actions boursières.

**Request**:
```json
{
  "symbols": ["AAPL", "MSFT", "GOOGL"]
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "comparison": { ... },
  "analyses": { ... }
}
```

---

### 5. Actualités - Market News

**Endpoint**: `GET /news`

Obtenir les actualités du marché avec analyse de sentiment.

**Query Parameters**:
- `limit` (optional, default: 20): Nombre d'articles

**Response** (200 OK):
```json
{
  "success": true,
  "articles": [ ... ],
  "sentiment": { ... }
}
```

---

### 6. Outils - Available Tools

**Endpoint**: `GET /tools`

Lister tous les outils MCP disponibles.

**Response** (200 OK):
```json
{
  "tools": [ ... ],
  "count": 3
}
```

---

### 7. Contexte - Clear Context

**Endpoint**: `DELETE /context/{user_id}`

Effacer le contexte conversationnel d'un utilisateur.

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Context cleared for user user123"
}
```

---

## 🔗 Exemples avec cURL

### Analyser une Action

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL"}'
```

### Envoyer un Message

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "Analyse Apple"
  }'
```

### Comparer des Actions

```bash
curl -X POST http://localhost:8000/api/compare \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL", "MSFT", "GOOGL"]
  }'
```

### Obtenir les Actualités

```bash
curl http://localhost:8000/api/news?limit=10
```

---

## 📊 Codes de Réponse HTTP

| Code | Signification |
|------|---------------|
| 200 | Succès |
| 400 | Requête invalide |
| 500 | Erreur serveur |
| 503 | Service indisponible |

---

## 📈 Recommandations

- **BUY**: Tendance bullish + sentiment positif
- **SELL**: Tendance bearish + sentiment négatif
- **HOLD**: Signaux mixtes

Confiance: 0-1 (plus élevé = plus confiant)

---

## 📞 Documentation Interactive

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
