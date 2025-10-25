# 📋 INSTRUCCIONES DE MIGRACIÓN

## ✅ COMPLETADO AUTOMÁTICAMENTE:
1. Backup de archivos .env antiguos en `backups/env_migration/`
2. Creación de nuevos archivos de configuración
3. Migración de credenciales funcionales de Supabase

## ⚠️ ACCIÓN REQUERIDA:

### 1. RENOMBRAR ARCHIVOS:
```bash
cd backend/config/environments
mv env.development.example .env.development
mv env.production.example .env.production
```

### 2. CONFIGURAR DESARROLLO:
Editar `backend/config/environments/.env.development`:
- Verificar que las credenciales de Supabase estén correctas
- Configurar email si necesario (o dejar MOCK_EMAIL_MODE=true)
- Configurar Google OAuth si necesario (o dejar vacío para modo mock)

### 3. CONFIGURAR PRODUCCIÓN:
Editar `backend/config/environments/.env.production`:
- Actualizar SECRET_KEY y SECURITY_PASSWORD_SALT con valores seguros
- Configurar credenciales reales de email
- Configurar Google OAuth con credenciales reales
- Verificar credenciales de Supabase

### 4. CAMBIAR AL NUEVO SISTEMA:
```bash
# Usar el nuevo sistema de configuración
cd backend
python scripts/env_manager.py switch development

# Verificar configuración
python scripts/system_diagnostic.py
```

### 5. LIMPIAR ARCHIVOS ANTIGUOS:
Una vez verificado que todo funciona:
```bash
# Eliminar archivos .env antiguos del directorio backend/
rm backend/.env*
```

## 📁 NUEVA ESTRUCTURA:
```
backend/
├── config/
│   ├── environments/
│   │   ├── .env.development    # Variables para desarrollo
│   │   ├── .env.production     # Variables para producción
│   │   ├── base.json           # Config compartida
│   │   ├── development.json    # Config de desarrollo
│   │   └── production.json     # Config de producción
│   ├── app_config.py           # Gestor de configuración
│   └── database_manager.py     # Gestor de conexiones
└── .env                        # Symlink al entorno activo
```
