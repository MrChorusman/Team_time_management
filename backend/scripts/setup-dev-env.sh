#!/bin/bash
# Script para configurar entorno de desarrollo
# Uso: ./setup-dev-env.sh [local|dev-prod]

set -e

echo "🔧 CONFIGURACIÓN DE ENTORNO DE DESARROLLO"
echo "=========================================="

# Determinar entorno
ENV_TYPE=${1:-"dev-prod"}

if [ "$ENV_TYPE" = "local" ]; then
    echo "📍 Configurando entorno LOCAL (PostgreSQL local)"
    ENV_FILE=".env.development"
elif [ "$ENV_TYPE" = "dev-prod" ]; then
    echo "📍 Configurando entorno DEV-PROD (Supabase desarrollo)"
    ENV_FILE=".env.development-production-like"
else
    echo "❌ Entorno no válido: $ENV_TYPE"
    echo "Uso: $0 [local|dev-prod]"
    exit 1
fi

# Verificar que el archivo existe
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Archivo $ENV_FILE no encontrado"
    exit 1
fi

# Crear backup del .env actual
if [ -f ".env" ]; then
    cp .env .env.backup
    echo "📦 Backup creado: .env.backup"
fi

# Copiar configuración
cp "$ENV_FILE" .env
echo "✅ Configuración copiada: $ENV_FILE → .env"

# Configuraciones específicas por entorno
if [ "$ENV_TYPE" = "local" ]; then
    echo ""
    echo "🗄️  CONFIGURACIÓN PARA DESARROLLO LOCAL:"
    echo "   1. Instalar PostgreSQL si no está instalado"
    echo "   2. Crear base de datos: createdb team_time_management_dev"
    echo "   3. Ejecutar: python main.py"
    
elif [ "$ENV_TYPE" = "dev-prod" ]; then
    echo ""
    echo "🌐 CONFIGURACIÓN PARA DESARROLLO CON SUPABASE:"
    echo "   1. Configurar variables SUPABASE_DEV_* en .env"
    echo "   2. Reemplazar [PROYECTO-DEV], [ANON-KEY-DEV], [PASSWORD-DEV]"
    echo "   3. Ejecutar: python main.py"
fi

echo ""
echo "🎯 PRÓXIMOS PASOS:"
echo "   1. Editar .env con tus credenciales"
echo "   2. Instalar dependencias: pip install -r requirements.txt"
echo "   3. Ejecutar aplicación: python main.py"
echo ""
echo "✅ Entorno de desarrollo configurado: $ENV_TYPE"
