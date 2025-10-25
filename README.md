# Team Time Management

Una aplicación web moderna y completa para la gestión de horarios empresariales con soporte global de festivos y funcionalidades avanzadas de control de tiempo.

## 🚀 Características Principales

- **Gestión Global de Empleados**: Soporte para empleados de cualquier país del mundo
- **Sistema de Festivos Automático**: Carga automática de festivos nacionales y regionales
- **Calendario Interactivo**: Gestión visual de vacaciones, ausencias y actividades
- **Roles y Permisos**: Sistema completo de roles (Admin, Manager, Employee, Viewer)
- **Notificaciones Inteligentes**: Centro de notificaciones y alertas automáticas
- **Reportes Exportables**: Exportación a PDF y CSV
- **Arquitectura Moderna**: React + Flask + Supabase

## 🏗️ Arquitectura

### Stack Tecnológico
- **Frontend**: React 18 + Vite + React Router
- **Backend**: Flask + SQLAlchemy + Flask-Security-Too
- **Base de Datos**: PostgreSQL (Supabase)
- **Autenticación**: Flask-Security-Too con validación de email
- **Despliegue**: Preparado para contenedores Docker

### Estructura del Proyecto
```
Team_time_management/
├── backend/                 # API Flask
│   ├── app/
│   ├── models/
│   ├── services/
│   └── requirements.txt
├── frontend/                # React App
│   ├── src/
│   ├── public/
│   └── package.json
├── docs/                    # Documentación
└── docker-compose.yml       # Configuración de contenedores
```

## 🌍 Funcionalidades Globales

### Sistema de Festivos
- **118 países** soportados
- Carga automática desde APIs gubernamentales
- Jerarquía: Nacional → Regional → Local
- Prevención de duplicados inteligente

### Gestión de Horarios
- Configuración flexible por empleado
- Horarios de verano/invierno
- Cálculos automáticos de horas trabajadas
- Proyecciones y análisis de tendencias

## 👥 Roles y Permisos

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| **Admin** | Administrador del sistema | Control total de la aplicación |
| **Manager** | Gestor de equipo | Gestión de su equipo y aprobaciones |
| **Employee** | Empleado estándar | Gestión de su calendario personal |
| **Viewer** | Usuario temporal | Solo acceso al formulario de registro |

## 📊 Funcionalidades Avanzadas

### Centro de Notificaciones
- Notificaciones internas en tiempo real
- Alertas de solapamiento de vacaciones
- Resúmenes automáticos por email

### Reportes y Análisis
- Dashboard con métricas globales
- Resumen personal anual
- Exportación a PDF/CSV
- Análisis de eficiencia por equipo

## 🚀 Instalación y Desarrollo

### Prerrequisitos
- Node.js 18+
- Python 3.11+
- PostgreSQL (o cuenta de Supabase)

### Configuración Rápida
```bash
# Clonar el repositorio
git clone https://github.com/MrChorusman/Team_time_management.git
cd Team_time_management

# Configurar backend
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configurar frontend
cd ../frontend
npm install

# Configurar entorno de desarrollo (NUEVO)
cd ../backend
python scripts/env_manager.py switch development
```

### 🆕 Nueva Arquitectura de Configuración

El proyecto ahora utiliza una **arquitectura de configuración centralizada** que simplifica significativamente la gestión de entornos:

#### Gestión de Entornos
```bash
# Ver entornos disponibles
python scripts/env_manager.py list

# Cambiar a desarrollo
python scripts/env_manager.py switch development

# Cambiar a producción
python scripts/env_manager.py switch production

# Ver configuración actual
python scripts/env_manager.py show

# Validar entorno
python scripts/env_manager.py validate development

# Probar conexiones
python scripts/env_manager.py test development
```

#### Diagnóstico del Sistema
```bash
# Diagnóstico completo del sistema
python scripts/system_diagnostic.py

# Pruebas de configuración
python scripts/test_new_config.py

# Auditar configuración actual
python scripts/audit_config.py
```

#### Migración de Configuración
```bash
# Migrar configuración existente
python scripts/migrate_env_config.py
```

### Variables de Entorno

La configuración ahora se maneja automáticamente a través de archivos específicos por entorno:

- **Desarrollo**: `backend/config/environments/.env.development`
- **Producción**: `backend/config/environments/.env.production`

**No es necesario** configurar manualmente variables de entorno. El sistema las gestiona automáticamente.

## 📱 Uso de la Aplicación

### Flujo de Registro
1. **Registro inicial**: Usuario se registra con email
2. **Verificación**: Confirmación por email obligatoria
3. **Perfil de empleado**: Completar datos laborales
4. **Aprobación**: Manager aprueba la incorporación
5. **Acceso completo**: Usuario activo con rol Employee

### Gestión del Calendario
- **Vacaciones (V)**: Días completos de vacaciones
- **Ausencias (A)**: Faltas por enfermedad o motivos personales
- **HLD**: Horas de Libre Disposición (parciales)
- **Guardia (G)**: Horas extra o guardias
- **Formación (F)**: Eventos de formación
- **Otros (C)**: Permisos y otros motivos

## 🔧 Desarrollo

### Comandos Útiles
```bash
# Ejecutar backend (con nueva configuración)
cd backend
python scripts/env_manager.py switch development
python main.py

# Ejecutar frontend
cd frontend && npm run dev

# Ejecutar tests
cd backend && python scripts/test_new_config.py
cd frontend && npm test

# Build para producción
cd frontend && npm run build
```

### 🆕 Comandos de la Nueva Arquitectura

#### Gestión de Entornos
```bash
# Listar entornos disponibles
python scripts/env_manager.py list

# Cambiar entorno
python scripts/env_manager.py switch <environment>

# Mostrar configuración
python scripts/env_manager.py show [environment]

# Validar configuración
python scripts/env_manager.py validate <environment>

# Probar conexiones
python scripts/env_manager.py test <environment>
```

#### Diagnóstico y Mantenimiento
```bash
# Diagnóstico completo
python scripts/system_diagnostic.py

# Pruebas de configuración
python scripts/test_new_config.py

# Auditar configuración
python scripts/audit_config.py

# Probar conexiones Supabase
python scripts/test_all_connections.py
```

#### Migración y Setup
```bash
# Migrar configuración existente
python scripts/migrate_env_config.py

# Crear nuevo entorno
python scripts/env_manager.py create <env_name> [template]
```

## 📚 Documentación

- [Nueva Arquitectura de Configuración](docs/NUEVA_ARQUITECTURA.md) 🆕
- [Guía de Instalación](docs/installation.md)
- [API Documentation](docs/api.md)
- [Guía de Usuario](docs/user-guide.md)
- [Arquitectura del Sistema](docs/architecture.md)

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙋‍♂️ Soporte

Si tienes preguntas o necesitas ayuda:
- Abre un [Issue](https://github.com/MrChorusman/Team_time_management/issues)
- Contacta al equipo de desarrollo

---

**Desarrollado con ❤️ por el equipo de Team Time Management**
