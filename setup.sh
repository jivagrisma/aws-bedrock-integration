#!/bin/bash

# Colores para mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Iniciando configuración del backend de AWS Bedrock...${NC}"

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker no está instalado. Por favor, instala Docker primero.${NC}"
    exit 1
fi

# Verificar si docker-compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Docker Compose no está instalado. Por favor, instala Docker Compose primero.${NC}"
    exit 1
fi

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creando archivo .env desde .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}Archivo .env creado. Por favor, actualiza las credenciales de AWS.${NC}"
fi

# Crear directorios necesarios
echo -e "${GREEN}Creando directorios necesarios...${NC}"
mkdir -p data

# Construir la imagen de Docker
echo -e "${GREEN}Construyendo imagen de Docker...${NC}"
docker-compose build

echo -e "${GREEN}Configuración completada.${NC}"
echo -e "${YELLOW}Para iniciar el servidor:${NC}"
echo -e "1. Edita el archivo .env con tus credenciales de AWS"
echo -e "2. Ejecuta: docker-compose up"
echo -e "\nPara probar la API:"
echo -e "curl http://localhost:8000/health"
echo -e "curl -X POST http://localhost:8000/api/llm/generate -H 'Content-Type: application/json' -d '{\"prompt\":\"Hola, ¿cómo estás?\"}'"