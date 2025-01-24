# AWS Bedrock Backend Integration

Backend para integración con AWS Bedrock y Claude 3.5 Sonnet, proporcionando una API REST para interactuar con el modelo de lenguaje.

## Características

- ✨ Integración completa con AWS Bedrock
- 🚀 API REST con FastAPI
- 🔄 Soporte para streaming de respuestas
- 💾 Caché de respuestas para optimización
- 🔒 Manejo seguro de credenciales
- 🐳 Dockerizado para fácil despliegue

## Requisitos Previos

- Docker y Docker Compose
- Credenciales de AWS con acceso a Bedrock
- Python 3.9+ (para desarrollo local)

## Configuración Rápida

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd backend
```

2. Ejecutar script de configuración:
```bash
./setup.sh
```

3. Configurar credenciales:
   - Editar el archivo `.env` con tus credenciales de AWS
   - Ajustar otras configuraciones según necesidades

4. Iniciar el servidor:
```bash
docker-compose up
```

## Estructura del Proyecto

```
backend/
├── src/
│   ├── bedrock/           # Cliente de AWS Bedrock
│   │   ├── client.py      # Cliente base
│   │   ├── config.py      # Configuración
│   │   └── models.py      # Modelos de datos
│   ├── services/          # Capa de servicios
│   │   └── llm_service.py # Servicio LLM
│   └── api/              # API REST
│       └── routes/       # Endpoints
├── .env.example          # Template de variables de entorno
├── Dockerfile            # Configuración de Docker
├── docker-compose.yml    # Configuración de Docker Compose
└── requirements.txt      # Dependencias Python
```

## API Endpoints

### Generación de Texto
```http
POST /api/llm/generate
Content-Type: application/json

{
    "prompt": "Explica la programación asíncrona",
    "system_prompt": "Eres un experto en programación",
    "temperature": 0.7,
    "max_tokens": 1000
}
```

### Chat
```http
POST /api/llm/chat
Content-Type: application/json

{
    "messages": [
        {"role": "user", "content": "¿Qué es Python?"}
    ],
    "temperature": 0.7
}
```

### Análisis de Código
```http
POST /api/llm/analyze-code
Content-Type: application/json

{
    "code": "def suma(a, b):\n    return a + b",
    "context": "Función simple de suma"
}
```

### Resumen de Texto
```http
POST /api/llm/summarize
Content-Type: application/json

{
    "text": "Texto largo para resumir...",
    "max_length": 100,
    "format": "bullet_points"
}
```

## Ejemplos de Uso

### Python con httpx
```python
import httpx

async def generate_text():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/llm/generate",
            json={
                "prompt": "Explica Docker en términos simples",
                "temperature": 0.7
            }
        )
        return response.json()
```

### cURL
```bash
# Generar texto
curl -X POST "http://localhost:8000/api/llm/generate" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Explica la programación asíncrona"}'

# Chat
curl -X POST "http://localhost:8000/api/llm/chat" \
    -H "Content-Type: application/json" \
    -d '{"messages": [{"role": "user", "content": "¿Qué es Python?"}]}'
```

## Configuración Avanzada

### Variables de Entorno

```env
# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_TEMPERATURE=0.0
BEDROCK_MAX_TOKENS=8192
```

### Caché y Optimización

El servicio implementa caché de respuestas para optimizar el rendimiento:

```python
# Usar caché
response = await llm_service.generate_text(
    prompt="Hello",
    use_cache=True
)

# Deshabilitar caché
response = await llm_service.generate_text(
    prompt="Hello",
    use_cache=False
)
```

## Desarrollo Local

1. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecutar servidor en modo desarrollo:
```bash
uvicorn src.main:app --reload
```

## Pruebas

Ejecutar pruebas:
```bash
pytest
```

Con cobertura:
```bash
pytest --cov=src tests/
```

## Solución de Problemas

### Error de Credenciales AWS
```
Error: Failed to generate response: AccessDeniedException
```
Solución: Verificar credenciales en .env y permisos de AWS.

### Error de Timeout
```
Error: Failed to generate response: ThrottlingException
```
Solución: Aumentar BEDROCK_TIMEOUT en .env o reducir la frecuencia de requests.

## Contribuir

1. Fork el repositorio
2. Crear rama para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## Licencia

MIT

## Soporte

- Abrir un issue en GitHub
- Consultar la [documentación de AWS Bedrock](https://docs.aws.amazon.com/bedrock/)
- Contactar al equipo de desarrollo