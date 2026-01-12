# Guide de Développement - StockAdvisor+ Bot Backend

## 🚀 Démarrage du Développement

### 1. Setup Initial

```bash
# Cloner le repository
git clone <repo-url>
cd stockadvisor-backend

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Copier et configurer .env
cp .env.example .env
# Éditer .env avec vos paramètres
```

### 2. Démarrer Ollama

```bash
# Dans un terminal séparé
ollama serve

# Télécharger un modèle (si nécessaire)
ollama pull mistral
```

### 3. Lancer le Backend

```bash
# Mode développement avec rechargement automatique
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Mode production
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## 📝 Conventions de Code

### Style de Code
- **PEP 8**: Respecter les standards Python
- **Type Hints**: Toujours utiliser les type hints
- **Docstrings**: Docstring sur toutes les fonctions/classes

### Exemple de Fonction

```python
async def analyze_stock(self, symbol: str) -> Dict[str, Any]:
    \"\"\"
    Perform complete stock analysis.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
    
    Returns:
        Dictionary containing analysis report
    
    Raises:
        ValueError: If symbol is invalid
    \"\"\"
    try:
        # Implementation
        pass
    except Exception as e:
        app_logger.error(f"Error analyzing {symbol}: {str(e)}")
        raise
```

### Exemple de Classe

```python
class MyAnalyzer:
    \"\"\"
    Description courte de la classe.
    
    Longer description if needed.
    \"\"\"
    
    def __init__(self, param: str):
        \"\"\"
        Initialize the analyzer.
        
        Args:
            param: Parameter description
        \"\"\"
        self.param = param
```

## 🧪 Tests

### Exécuter les Tests

```bash
# Tous les tests
pytest tests/ -v

# Tests spécifiques
pytest tests/test_analyzer.py -v

# Avec couverture
pytest tests/ --cov=src --cov-report=html

# Tests avec marqueurs
pytest -m unit  # Uniquement les tests unitaires
pytest -m integration  # Uniquement les tests d'intégration
```

### Écrire des Tests

```python
import pytest
from src.mcp.tools.analyzer import TechnicalAnalyzer

class TestTechnicalAnalyzer:
    \"\"\"Tests for TechnicalAnalyzer.\"\"\"
    
    @pytest.fixture
    def analyzer(self):
        \"\"\"Create an analyzer instance for testing.\"\"\"
        return TechnicalAnalyzer()
    
    def test_calculate_moving_average(self, analyzer):
        \"\"\"Test moving average calculation.\"\"\"
        prices = [100, 102, 101, 103, 105]
        ma = analyzer.calculate_moving_average(prices, period=3)
        
        assert len(ma) > 0
        assert all(isinstance(x, float) for x in ma)
```

### Marqueurs de Test

```python
# Marqueur unitaire
@pytest.mark.unit
def test_something():
    pass

# Marqueur d'intégration
@pytest.mark.integration
def test_integration():
    pass

# Marqueur pour tests lents
@pytest.mark.slow
def test_slow_operation():
    pass
```

## 📚 Ajouter une Nouvelle Fonctionnalité

### 1. Créer un Nouvel Outil MCP

```python
# src/mcp/tools/my_tool.py
class MyTool:
    \"\"\"Description of my tool.\"\"\"
    
    async def do_something(self, param: str) -> Dict[str, Any]:
        \"\"\"
        Do something useful.
        
        Args:
            param: Parameter
        
        Returns:
            Result dictionary
        \"\"\"
        try:
            # Implementation
            result = {}
            return result
        except Exception as e:
            app_logger.error(f"Error: {str(e)}")
            raise
```

### 2. Ajouter l'Outil au MCP Server

```python
# src/mcp/server.py
from .tools.my_tool import MyTool

class MCPServer:
    def __init__(self):
        self.my_tool = MyTool()
    
    async def use_my_tool(self, param: str) -> Dict[str, Any]:
        \"\"\"Use my tool.\"\"\"
        return await self.my_tool.do_something(param)
```

### 3. Ajouter un Endpoint API

```python
# src/api/routes.py
@router.post(\"/my-endpoint\")
async def my_endpoint(request: MyRequest):
    \"\"\"
    My endpoint description.
    
    Args:
        request: Request data
    
    Returns:
        Response data
    \"\"\"
    try:
        result = await mcp_server.use_my_tool(request.param)
        return {\"success\": True, \"data\": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 4. Ajouter des Tests

```python
# tests/test_my_tool.py
import pytest
from src.mcp.tools.my_tool import MyTool

class TestMyTool:
    @pytest.fixture
    def tool(self):
        return MyTool()
    
    def test_do_something(self, tool):
        result = tool.do_something("test")
        assert result is not None
```

## 🔍 Debugging

### Logging

```python
from src.utils.logger import app_logger

# Différents niveaux
app_logger.debug("Debug message")
app_logger.info("Info message")
app_logger.warning("Warning message")
app_logger.error("Error message")
app_logger.critical("Critical message")
```

### Debugging avec pdb

```python
import pdb

def my_function():
    pdb.set_trace()  # Breakpoint
    # Code
```

### Vérifier les Logs

```bash
# Voir les logs en temps réel
tail -f logs/app.log

# Filtrer les logs par niveau
grep ERROR logs/app.log
grep WARNING logs/app.log
```

## 🔧 Configuration

### Variables d'Environnement

```bash
# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DEBUG=True

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral

# Frontend
FRONTEND_URL=http://localhost:3000

# Scraping
SCRAPING_DELAY=2
SCRAPING_TIMEOUT=10
MAX_RETRIES=3
```

### Modifier la Configuration

1. Éditer `.env`
2. Redémarrer le serveur
3. Les changements seront appliqués

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/api/health
```

### Endpoints Disponibles

```bash
# Lister les outils
curl http://localhost:8000/api/tools

# Analyser une action
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL"}'

# Envoyer un message
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user1", "message": "Analyse Apple"}'
```

## 🚀 Optimisations

### Performance

1. **Caching**: Mettre en cache les résultats
2. **Async**: Utiliser async/await pour I/O
3. **Batch**: Traiter les requêtes par batch
4. **Connection Pooling**: Réutiliser les connexions

### Exemple de Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(param: str) -> str:
    \"\"\"Cached expensive operation.\"\"\"
    return result
```

## 📦 Dépendances

### Ajouter une Dépendance

```bash
# Ajouter une dépendance
pip install package-name

# Mettre à jour requirements.txt
pip freeze > requirements.txt
```

### Vérifier les Dépendances

```bash
# Lister les dépendances
pip list

# Vérifier les vulnérabilités
pip install safety
safety check
```

## 🔐 Sécurité

### Bonnes Pratiques

1. **Ne jamais commiter les secrets**: Utiliser `.env`
2. **Valider les entrées**: Utiliser Pydantic
3. **Gérer les erreurs**: Ne pas exposer les détails
4. **Logging sécurisé**: Ne pas logger les secrets

### Exemple de Validation

```python
from pydantic import BaseModel, Field, validator

class StockRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    
    @validator('symbol')
    def symbol_must_be_uppercase(cls, v):
        if not v.isupper():
            raise ValueError('Symbol must be uppercase')
        return v
```

## 📖 Documentation

### Générer la Documentation

```bash
# Swagger UI
http://localhost:8000/docs

# ReDoc
http://localhost:8000/redoc
```

### Documenter les Endpoints

```python
@router.post(\"/endpoint\", response_model=ResponseModel)
async def my_endpoint(request: RequestModel):
    \"\"\"
    Endpoint description.
    
    Longer description if needed.
    
    Args:
        request: Request data
    
    Returns:
        Response data
    
    Raises:
        HTTPException: If something goes wrong
    \"\"\"
    pass
```

## 🐛 Troubleshooting

### Ollama ne répond pas

```bash
# Vérifier que Ollama est en cours d'exécution
curl http://localhost:11434/api/tags

# Redémarrer Ollama
pkill ollama
ollama serve
```

### Erreur de connexion

```bash
# Vérifier la configuration
cat .env

# Vérifier les ports
netstat -tuln | grep 8000
netstat -tuln | grep 11434
```

### Tests qui échouent

```bash
# Exécuter avec plus de verbosité
pytest tests/ -vv

# Afficher les prints
pytest tests/ -s

# Arrêter au premier échec
pytest tests/ -x
```

## 📝 Checklist de Commit

- [ ] Code suit les conventions
- [ ] Type hints présents
- [ ] Docstrings complètes
- [ ] Tests écrits et passants
- [ ] Pas de secrets en dur
- [ ] Logs appropriés
- [ ] Pas de code mort
- [ ] Pas de imports inutilisés

## 🎯 Prochaines Étapes

1. Ajouter la persistance des données
2. Implémenter le caching distribué
3. Ajouter des tests d'intégration
4. Configurer le CI/CD
5. Mettre en place le monitoring
