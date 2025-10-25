# 🔧 GUÍA DE SEPARACIÓN DE ENTORNOS - Team Time Management

## 📋 **RESUMEN**

Esta guía explica cómo usar la nueva configuración de entornos separados para desarrollo y producción, asegurando que no haya conflictos entre ambos.

## 🏗️ **ARQUITECTURA DE ENTORNOS**

### **Entornos Disponibles:**

1. **`local`** - Desarrollo con PostgreSQL local
2. **`dev-prod`** - Desarrollo con Supabase (simula producción)
3. **`production`** - Producción (SOLO para Render)

### **Estructura de Archivos:**

```
backend/
├── .env.production              # Producción (NO TOCAR)
├── .env.development             # Desarrollo local
├── .env.development-production-like  # Desarrollo con Supabase
├── .env                         # Enlace al entorno activo
├── config.py                    # Configuración multi-entorno
├── supabase_config.py           # Configuración Supabase extendida
└── scripts/
    ├── switch-env.py            # Cambiar entre entornos
    ├── setup-dev-env.sh         # Configurar entorno dev
    └── deploy-check.py          # Verificar antes de deploy
```

## 🚀 **CONFIGURACIÓN INICIAL**

### **Paso 1: Crear Proyecto Supabase de Desarrollo**

1. Ve a [Supabase Dashboard](https://supabase.com/dashboard)
2. Crea un nuevo proyecto:
   - **Nombre**: `team-time-management-dev`
   - **Región**: `eu-west-3`
   - **Contraseña**: Genera una nueva
3. Anota estos datos:
   - URL del proyecto
   - Clave anónima (anon key)
   - Contraseña de la base de datos

### **Paso 2: Configurar Variables de Desarrollo**

Edita `.env.development-production-like`:

```bash
# Reemplazar estos valores con los del proyecto de desarrollo
SUPABASE_DEV_URL=https://tu-proyecto-dev.supabase.co
SUPABASE_DEV_KEY=tu-anon-key-dev
SUPABASE_DEV_DB_PASSWORD=tu-password-dev
SUPABASE_DEV_USER=postgres.tu-proyecto-dev
```

## 🔄 **GESTIÓN DE ENTORNOS**

### **Cambiar Entre Entornos:**

```bash
# Desarrollo local (PostgreSQL local)
python scripts/switch-env.py local

# Desarrollo con Supabase (simula producción)
python scripts/switch-env.py dev-prod

# Producción (SOLO para despliegues)
python scripts/switch-env.py production
```

### **Configurar Entorno de Desarrollo:**

```bash
# Configurar desarrollo con Supabase
./scripts/setup-dev-env.sh dev-prod

# Configurar desarrollo local
./scripts/setup-dev-env.sh local
```

## 📊 **MIGRACIÓN DE DATOS**

### **Migrar Datos de Producción a Desarrollo:**

Una vez creado el proyecto de desarrollo, ejecuta:

```bash
# 1. Cambiar a entorno de desarrollo
python scripts/switch-env.py dev-prod

# 2. Ejecutar migración (script personalizado)
python migrate_prod_to_dev.py
```

### **Script de Migración:**

```python
# migrate_prod_to_dev.py
import os
import psycopg2
from dotenv import load_dotenv

def migrate_data():
    # Conectar a producción
    prod_conn = psycopg2.connect(
        host=os.environ.get('SUPABASE_HOST'),
        port=os.environ.get('SUPABASE_PORT'),
        database=os.environ.get('SUPABASE_DB'),
        user=os.environ.get('SUPABASE_USER'),
        password=os.environ.get('SUPABASE_DB_PASSWORD')
    )
    
    # Conectar a desarrollo
    dev_conn = psycopg2.connect(
        host=os.environ.get('SUPABASE_DEV_HOST'),
        port=os.environ.get('SUPABASE_DEV_PORT'),
        database=os.environ.get('SUPABASE_DEV_DB'),
        user=os.environ.get('SUPABASE_DEV_USER'),
        password=os.environ.get('SUPABASE_DEV_DB_PASSWORD')
    )
    
    # Migrar datos (ejemplo)
    # ... código de migración ...
    
    print("✅ Migración completada")

if __name__ == "__main__":
    migrate_data()
```

## 🔒 **SEGURIDAD Y DESPLIEGUES**

### **Verificar Antes de Desplegar:**

```bash
# Verificar configuración de producción
python scripts/deploy-check.py
```

### **Reglas de Seguridad:**

1. **NUNCA** hacer commit de archivos `.env` con datos reales
2. **NUNCA** usar configuración de desarrollo en producción
3. **SIEMPRE** verificar con `deploy-check.py` antes de desplegar
4. **SIEMPRE** usar `production` solo para despliegues en Render

### **Flujo de Despliegue Seguro:**

```bash
# 1. Desarrollo
python scripts/switch-env.py dev-prod
python main.py  # Probar localmente

# 2. Commit y merge
git add -A
git commit -m "Nueva funcionalidad"
git checkout main
git merge feature-branch

# 3. Verificar antes de push
python scripts/deploy-check.py

# 4. Push (despliega automáticamente en Render)
git push origin main
```

## 🧪 **TESTING POR ENTORNO**

### **Desarrollo Local:**

```bash
# Configurar entorno local
python scripts/switch-env.py local

# Crear base de datos local
createdb team_time_management_dev

# Ejecutar aplicación
python main.py
```

### **Desarrollo con Supabase:**

```bash
# Configurar entorno dev-prod
python scripts/switch-env.py dev-prod

# Verificar conexión
curl http://localhost:5001/api/health

# Probar login
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"test123"}'
```

## 📋 **COMANDOS ÚTILES**

### **Verificar Estado del Entorno:**

```bash
# Ver configuración actual
cat .env | grep -E "(FLASK_ENV|SUPABASE|DEBUG)"

# Verificar conexión
python -c "from supabase_config import SupabaseConfig; print(SupabaseConfig.is_development_configured())"
```

### **Backup y Restauración:**

```bash
# Crear backup
cp .env .env.backup

# Restaurar backup
cp .env.backup .env
```

## ⚠️ **ADVERTENCIAS IMPORTANTES**

### **NUNCA HACER:**

- ❌ Usar configuración de desarrollo en producción
- ❌ Hacer commit de archivos `.env` con datos reales
- ❌ Modificar `.env.production` sin autorización
- ❌ Desplegar sin verificar con `deploy-check.py`

### **SIEMPRE HACER:**

- ✅ Usar entornos separados para desarrollo y producción
- ✅ Verificar configuración antes de desplegar
- ✅ Hacer backup antes de cambiar entornos
- ✅ Documentar cambios en configuración

## 🆘 **SOLUCIÓN DE PROBLEMAS**

### **Error: "SUPABASE_DEV_DB_PASSWORD no está configurado"**

```bash
# Verificar variables de entorno
python -c "import os; print(os.environ.get('SUPABASE_DEV_DB_PASSWORD'))"

# Configurar entorno correcto
python scripts/switch-env.py dev-prod
```

### **Error: "Connection refused"**

```bash
# Verificar configuración
python scripts/deploy-check.py

# Cambiar a entorno local
python scripts/switch-env.py local
```

### **Error: "Entorno no válido"**

```bash
# Ver entornos disponibles
python scripts/switch-env.py --help

# Usar entorno correcto
python scripts/switch-env.py dev-prod
```

## 📞 **SOPORTE**

Si tienes problemas con la configuración:

1. Verifica que todos los archivos `.env.*` existan
2. Ejecuta `python scripts/deploy-check.py`
3. Revisa los logs del backend
4. Consulta esta documentación

---

**✅ Con esta configuración tienes entornos completamente separados y seguros para desarrollo y producción.**
