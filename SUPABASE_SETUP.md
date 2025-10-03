# 🔧 Configuración de Supabase PostgreSQL

Este documento explica cómo configurar y migrar la aplicación Team Time Management para usar Supabase PostgreSQL como base de datos.

## 📋 Prerrequisitos

1. **Cuenta de Supabase**: Crear una cuenta en [supabase.com](https://supabase.com)
2. **Proyecto Supabase**: Crear un nuevo proyecto
3. **Credenciales**: Obtener las credenciales del proyecto

## 🔑 Variables de Entorno Requeridas

Crear un archivo `.env` en el directorio `backend/` con las siguientes variables:

```bash
# ===========================================
# CONFIGURACIÓN DE SUPABASE
# ===========================================

# URL de tu proyecto Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co

# Clave de servicio de Supabase (para operaciones del servidor)
SUPABASE_KEY=tu_service_role_key_aqui

# Configuración de base de datos PostgreSQL
SUPABASE_DB_PASSWORD=tu_contraseña_de_base_de_datos
SUPABASE_HOST=db.tu-proyecto.supabase.co
SUPABASE_PORT=5432
SUPABASE_DB_NAME=postgres

# URL completa de conexión a la base de datos
DATABASE_URL=postgresql://postgres:tu_contraseña@db.tu-proyecto.supabase.co:5432/postgres

# ===========================================
# CONFIGURACIÓN DE SEGURIDAD
# ===========================================

# Clave secreta para Flask (cambiar en producción)
SECRET_KEY=tu-clave-secreta-muy-segura

# Salt para Flask-Security
SECURITY_PASSWORD_SALT=tu-salt-de-seguridad

# ===========================================
# CONFIGURACIÓN DE EMAIL
# ===========================================

# Configuración SMTP para emails
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-contraseña-de-aplicacion

# ===========================================
# CONFIGURACIÓN DE REDIS (OPCIONAL)
# ===========================================

# URL de Redis para sesiones y caché
REDIS_URL=redis://localhost:6379/0

# ===========================================
# CONFIGURACIÓN DE LOGGING
# ===========================================

# Nivel de logging (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# ===========================================
# CONFIGURACIÓN DE ENTORNO
# ===========================================

# Entorno de ejecución (development, production, testing)
FLASK_ENV=development
DEBUG=true
```

## 🚀 Proceso de Migración

### Paso 1: Configurar Variables de Entorno

1. Ir al panel de Supabase
2. Navegar a **Settings** → **API**
3. Copiar la **URL** del proyecto
4. Copiar la **service_role** key (clave secreta)
5. Navegar a **Settings** → **Database**
6. Copiar la **Database Password**

### Paso 2: Ejecutar Script de Migración

```bash
cd backend
python migrate_to_supabase.py
```

### Paso 3: Verificar Migración

El script verificará automáticamente:
- ✅ Configuración de variables de entorno
- ✅ Conexión a Supabase
- ✅ Creación de tablas
- ✅ Migración de datos
- ✅ Verificación final

## 📊 Estructura de la Base de Datos

### Tablas Principales

1. **user**: Usuarios del sistema
2. **role**: Roles de usuario (admin, manager, employee, viewer)
3. **roles_users**: Relación many-to-many entre usuarios y roles
4. **employee**: Información de empleados
5. **team**: Equipos de trabajo
6. **holiday**: Días festivos globales
7. **calendar_activity**: Actividades del calendario
8. **notification**: Notificaciones del sistema

### Índices Optimizados

- `idx_holiday_date_country`: Optimización de consultas de festivos
- `idx_holiday_country_region`: Búsquedas por región
- `idx_holiday_location`: Búsquedas por ubicación completa

## 🔒 Consideraciones de Seguridad

### Variables de Entorno

- **NUNCA** subir el archivo `.env` al repositorio
- Usar valores seguros para `SECRET_KEY` y `SECURITY_PASSWORD_SALT`
- Rotar las claves regularmente en producción

### Supabase

- Usar **service_role** key solo en el servidor
- Configurar **Row Level Security (RLS)** si es necesario
- Habilitar **SSL** para todas las conexiones

## 🧪 Testing

### Verificar Conexión

```bash
cd backend
python -c "
from supabase_config import SupabaseConfig
print('Configuración:', SupabaseConfig.is_configured())
print('URL:', SupabaseConfig.get_database_url())
"
```

### Verificar Tablas

```bash
cd backend
python -c "
from app import create_app
from models.user import db, User
app = create_app()
with app.app_context():
    print('Usuarios:', User.query.count())
"
```

## 🚨 Troubleshooting

### Error: "SUPABASE_DB_PASSWORD no está configurado"

- Verificar que el archivo `.env` existe
- Verificar que la variable está definida correctamente
- Reiniciar la aplicación después de cambios en `.env`

### Error: "Connection refused"

- Verificar la URL de conexión
- Verificar que el proyecto Supabase está activo
- Verificar credenciales de acceso

### Error: "Table already exists"

- Las tablas ya existen en Supabase
- Esto es normal si ya se ejecutó la migración anteriormente
- El script maneja esto automáticamente

## 📈 Monitoreo

### Métricas Importantes

- **Conexiones activas**: Monitorear el uso de conexiones
- **Tiempo de respuesta**: Verificar latencia de consultas
- **Espacio usado**: Controlar el crecimiento de la base de datos

### Logs

- Habilitar logging en la aplicación
- Revisar logs de Supabase en el dashboard
- Monitorear errores de conexión

## 🔄 Backup y Recuperación

### Backup Automático

Supabase incluye backups automáticos:
- **Diarios**: Para proyectos gratuitos
- **Cada hora**: Para proyectos Pro

### Backup Manual

```bash
# Exportar datos específicos
pg_dump -h db.tu-proyecto.supabase.co -U postgres -d postgres > backup.sql

# Restaurar datos
psql -h db.tu-proyecto.supabase.co -U postgres -d postgres < backup.sql
```

## 📞 Soporte

### Recursos Útiles

- [Documentación de Supabase](https://supabase.com/docs)
- [Guía de PostgreSQL](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

### Contacto

Para problemas específicos de la aplicación:
- Revisar logs de la aplicación
- Verificar configuración de variables de entorno
- Consultar documentación de Supabase

---

**¡La migración a Supabase está completa! 🎉**
